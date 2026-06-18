# Research: sources/distributed-fs/ceph-client/tools/perf/builtin-top.c

## Purpose

`builtin-top.c` implements `perf top`, the live interactive profiler that continuously samples one or more perf events, resolves samples to symbols, aggregates them in histograms, and refreshes either a stdio or TUI display. It combines record-like event setup with report-like symbol, callchain, annotation, sorting, filtering, and browser functionality, but it runs continuously against mmap ring buffers instead of processing a completed `perf.data` file.

The file owns command-line parsing, default event setup, target/map creation, counter opening/mmap setup, live sample ingestion, ordered event processing, display threads, keyboard controls, source annotation updates, and cleanup.

## Important APIs, Types, and State

Most command state is stored in `struct perf_top`, defined in shared headers and initialized in `cmd_top()`. Fields used heavily here include:

- `evlist`, `session`, `tool`, and optional `sb_evlist` for the main event set and side-band BPF events.
- `record_opts`, including target, mmap pages, sampling frequency/period, overwrite mode, branch stack settings, namespace/cgroup tracking, and BPF event settings.
- Display controls such as `delay_secs`, `print_entries`, `winsize`, `min_percent`, `count_filter`, `zero`, `use_tui`, `use_stdio`, and hide-user/kernel flags.
- Annotation controls including `sym_filter`, `sym_filter_entry`, `sym_evsel`, `max_stack`, `stitch_lbr`, and vmlinux warning state.
- Sample/loss/drop counters such as `samples`, `kernel_samples`, `us_samples`, `guest_*`, `exact_samples`, `lost`, `lost_total`, `drop`, and `drop_total`.
- Ordered-event queue state `qe`, with two `ordered_events` buffers, a mutex, condition variable, input queue pointer, and rotate flag.

Local globals:

- `done` ends collection/display.
- `resize` records `SIGWINCH` events for terminal resize handling.
- `last_timestamp` tracks the newest sample timestamp seen by mmap reading and drives stale-event dropping.

Important function groups:

- Display sizing and stdio output: `perf_top__update_print_entries()`, `winch_sig()`, `perf_top__resize()`, `perf_top__print_sym_table()`, `perf_top__resort_hists()`.
- Annotation and source view: `perf_top__parse_source()`, `__zero_source_counters()`, `ui__warn_map_erange()`, `perf_top__record_precise_ip()`, `perf_top__show_details()`.
- Interactive key handling: prompt helpers, `perf_top__print_mapped_keys()`, `perf_top__key_mapped()`, `perf_top__handle_keypress()`.
- Threads: `display_thread_tui()`, `display_thread()`, `process_thread()`, `init_process_thread()`, `exit_process_thread()`.
- Sample processing: `perf_event__process_sample()`, `hist_iter__top_callback()`, lost-event handlers, `deliver_event()`.
- Ring-buffer reading: `perf_top__mmap_read_idx()`, `perf_top__mmap_read()`.
- Counter setup: `perf_top__overwrite_check()`, `perf_top_overwrite_fallback()`, `perf_top__start_counters()`.
- Entry point and option setup: `cmd_top()`, `__cmd_top()`, config and callchain parsers.

## Control Flow

`cmd_top()` is the entry point. It initializes histogram and annotation subsystems, creates an evlist, loads config via `perf_config()`, captures host environment and CPUID for annotation, parses a large option table, validates symbol/annotation/target arguments, defaults to system-wide mode if no target is provided, creates default events when the user did not provide `-e`, initializes event switching, resolves incompatible hierarchy/fields and LBR/callchain combinations, configures branch/callchain behavior, sets sort mode to top, chooses stdio or TUI browser mode, creates an in-memory `perf_session`, sets up sorting and uid filters, creates CPU/thread maps, configures record options, initializes symbol/annotation support, creates optional BPF side-band events, starts the side-band thread, and then calls `__cmd_top()`.

`__cmd_top()` performs runtime setup:

1. Resolve `objdump` if annotation needs it.
2. Register callchain parameters when enabled.
3. Register the idle thread and enable multithreaded mode for thread synthesis.
4. Initialize the ordered-event processing queues.
5. Configure namespace/cgroup event processing flags.
6. Synthesize existing BPF, cgroup, and thread metadata into the session.
7. Read CPU topology when socket output requires it.
8. Uniquify event names and open/mmap counters with `perf_top__start_counters()`.
9. Set ID header sizes and enable events for non-empty targets.
10. Start the processing thread and a display thread.
11. Optionally set realtime scheduling priority.
12. Poll once, read initial mmap data, then loop reading mmaps and polling until `done`.
13. Join display and process threads, restore single-threaded mode, and release ordered-event queues.

`perf_top__start_counters()` applies record options to the evlist, checks that all events agree on overwrite mode, opens each evsel, handles overwrite fallback if `write_backward` is unsupported, applies generic evsel fallbacks, applies filters, and mmaps the evlist.

The data path starts in `perf_top__mmap_read()`. For overwrite mode it toggles backward mmap state, then iterates each mmap and calls `perf_top__mmap_read_idx()`. That function initializes mmap reading, reads raw events, parses timestamps into `last_timestamp`, queues copied events into the current ordered-events input queue, consumes mmap data, and coordinates queue rotation with the processing thread.

`process_thread()` watches the active queue. When events are available, it swaps input queues with `rotate_queues()`, asks the reader to stop using the old queue through a condition variable handshake, and flushes the old queue with `ordered_events__flush(..., OE_FLUSH__TOP)`. `deliver_event()` is the ordered-events callback.

`deliver_event()` drops stale sample events that are more than `delay_secs` behind `last_timestamp`, parses samples, maps sample IDs to evsels, applies event switching, increments counters by CPU mode, chooses the host or guest machine, honors hide-user/kernel flags, dispatches samples to `perf_event__process_sample()`, accounts lost events, or passes metadata events to `machine__process_event()`.

`perf_event__process_sample()` resolves the sample to an address location, handles guest/missing-machine cases, warns about restricted kernel symbols or missing vmlinux data, enables LBR stitching on the thread when requested, and adds the sample to the evsel histograms under the hists lock via `hist_entry_iter__add()`. The add-entry callback records precise IP data for annotation and accounts branch cycles.

Display has two modes:

- `display_thread()` is the stdio mode. It unshares `CLONE_FS` for namespace symbol access, installs signal handlers, sets quiet terminal input, repeatedly prints the symbol table, polls stdin for keypresses, and applies interactive changes such as delay, entry count, active event, filters, hide flags, symbol annotation, and zeroing.
- `display_thread_tui()` is the TUI mode. It repeatedly resorts hists, sets uid filters, calls `evlist__tui_browse_hists()`, handles reload by zeroing, and stops the profiler on exit.

`perf_top__resort_hists()` decays or deletes entries when events are enabled depending on `zero`, collapses hists, matches group members to leaders, and output-resorts each evsel. `perf_top__print_sym_table()` clears the console, prints the top header, warns on newly observed lost chunks, and either shows annotation details or recalculates column widths and prints histogram rows.

## State and Persistence Behavior

`perf top` is intentionally live and does not write a normal `perf.data` file from this implementation. Persistent effects are limited to terminal display, optional symbol/annotation subprocess/tool lookups, and live perf-event kernel state while counters are open. Runtime state lives in:

- Kernel perf_event fds and mmap buffers owned by evsels/evlist.
- In-memory histograms under each evsel.
- In-memory symbol, map, DSO, machine, cgroup, namespace, BPF, and thread metadata in `perf_session`.
- Two copied ordered-event queues used to decouple mmap reading from event processing.
- Terminal state managed by `set_term_quiet_input()`/`tcsetattr()` in stdio display mode.

The command can start side-band BPF event collection through `sb_evlist`; this is stopped after `__cmd_top()` unless BPF events were disabled. Display-thread signal handlers set `done`/`session_done` rather than directly tearing down counters.

## Dependencies and Integration Points

Major dependencies:

- Event setup and mmap: `util/evlist.h`, `util/evsel.h`, `util/evsel_config.h`, `util/mmap.h`, libperf `perf/mmap.h`, `record_opts__config()`.
- Session/machine/symbols: `util/session.h`, `util/machine.h`, `util/map.h`, `util/dso.h`, `util/symbol.h`, `util/synthetic-events.h`.
- Histograms/report UI: `util/top.h`, `util/sort.h`, `util/annotate.h`, `ui/ui.h`, TUI browser APIs, hists and hist-entry iteration.
- Callchains and branches: `util/callchain.h`, `util/parse-branch-options.h`, LBR stitching support, branch cycle accounting.
- Targets, cgroups, uid filters, namespaces, BPF metadata: `util/cgroup.h`, `util/bpf-event.h`, `util/intlist.h`, `evswitch`.
- CLI/config: `subcmd/parse-options.h`, `perf_config()`, `perf_default_config()`, annotation config helpers.
- Platform helpers: `arch/common.h`, `dwarf-regs.h`, `sysctl__max_stack()`, scheduler/terminal/signal syscalls.

The file integrates with both record-style configuration and report-style presentation. This makes option interactions delicate: changing defaults or record options can affect mmap setup, sample IDs, sorting fields, annotation, callchains, and UI output at the same time.

## Risks and Edge Cases

- `done`, `resize`, and `last_timestamp` are shared across threads with minimal synchronization. Existing design relies on simple signal-safe flags and queue synchronization; deeper changes must avoid races with mmap reading and event flushing.
- Ordered queue rotation uses a condition-variable handshake between the reader and process thread. If the rotate flag or signal order changes, the processing thread can stall or read from a queue still being appended.
- `should_drop()` drops samples older than `delay_secs` relative to the newest timestamp. This protects interactivity but can bias output under heavy load.
- Overwrite mode must be consistent across all events. Mixed per-event overwrite terms are rejected; fallback from overwrite to non-overwrite only happens when the first event reveals missing kernel support.
- Annotation updates lock per-symbol annotations while hists locks may also be held. `perf_top__record_precise_ip()` explicitly unlocks hists before sleeping on warnings; lock-order changes are risky.
- Missing or restricted kernel symbols are warned lazily on first unresolved kernel samples. This means tests must trigger actual samples to cover those paths.
- Stdio mode manipulates terminal attributes and must restore them on exits from key handling, signal paths, and normal shutdown.
- TUI and stdio display paths share histogram state but have different refresh mechanics; changes to resorting/zeroing must preserve both.
- `target__none()` defaults to system-wide mode, so permission failures are common on restrictive kernels and should produce clear errors through `evsel__open_strerror()`.
- BPF side-band setup is optional and best-effort; failures should not prevent profiling, but they reduce BPF symbol resolution.

## Test Signals

Useful validation signals include:

- `perf top --stdio -d 1 -E 5` or a short controlled run under a timeout wrapper to exercise stdio refresh and counter setup.
- `perf top -e cycles`, grouped events, and invalid/unsupported events for open fallback and error messages.
- `perf top --overwrite` on kernels with and without backward mmap support to validate fallback.
- `perf top -p <pid>` and `perf top -a -C <cpu>` to validate target maps.
- Interactive stdio keys: `d`, `e`, `E`, `f`, `F`, `K`, `U`, `s`, `S`, `z`, and `q`.
- `perf top --tui` where slang support is built, to cover TUI browse/reload behavior.
- `perf top -g`, `--call-graph`, `--children`, branch options, and `--stitch-lbr` to cover callchain/branch validation and histogram accounting.
- `perf top --sym-annotate <symbol>`, `--objdump`, and `--addr2line` for annotation initialization and source counters.
- `--uid`, `--cgroup`, `--all-cgroups`, `--namespaces`, and BPF-event paths where kernel/build support exists.
- Heavy sampling or constrained mmap pages to trigger lost/drop warnings and stale-event dropping.
