# sources/distributed-fs/ceph-client/tools/perf/builtin-kvm.c

## Purpose

`builtin-kvm.c` implements the `perf kvm` command family. At the top level it wraps ordinary `perf record`, `perf report`, `perf top`, `perf diff`, and `perf buildid-list` so host/guest defaults and KVM-specific data file names are applied. When libtraceevent support is available it also implements `perf kvm stat`, including offline `record`/`report` and timerfd-driven live reporting of KVM tracepoints such as VM exits, MMIO, and IO port events.

## Important APIs, Types, and Functions

The primary state type is `struct perf_kvm_stat` from `util/kvm-stat.h`, which carries the perf tool callbacks, session, evlist, target options, selected report event, sort key, VCPU filter, totals, event decoding operations, and live-display settings. `struct kvm_event` stores one histogram row with an event key, a `hist_entry`, total timing/count stats, per-VCPU stats, and a back pointer to the active `perf_kvm_stat`. `struct vcpu_event_record` is attached to each perf thread via `thread__priv()` and tracks the active begin event and timestamp for that VCPU thread.

Histogram output is configured through `struct kvm_dimension`, `struct kvm_fmt`, and the global `kvm_hists`. `kvm_hpp_list__parse()`, `get_format()`, and `kvm_hists__reinit()` adapt KVM dimensions to perf hpp columns and sort fields. KVM event matching flows through architecture hooks registered by `register_kvm_events_ops()`, which selects `kvm->events_ops` from `kvm_reg_events_ops(e_machine)`.

Important processing functions include `find_create_kvm_event()`, `handle_begin_event()`, `handle_child_event()`, `handle_end_event()`, `handle_kvm_event()`, `process_sample_event()`, `read_events()`, `kvm_events_report_vcpu()`, `kvm_events_record()`, `kvm_events_live()`, `perf_kvm__mmap_read()`, and `perf_kvm__handle_timerfd()`. Top-level dispatch is in `cmd_kvm()`, with wrapper helpers `__cmd_record()`, `__cmd_report()`, `__cmd_buildid_list()`, `__cmd_top()`, and `kvm_cmd_stat()`.

## Control Flow

`cmd_kvm()` parses global KVM options, defaults to guest collection unless host is explicitly requested, chooses a file name such as `perf.data.guest`, `perf.data.host`, or `perf.data.kvm`, then dispatches to the requested subcommand. The non-stat subcommands mostly build a new argv array and call the corresponding builtin. `__cmd_record()` and `__cmd_top()` add default architecture events through `kvm_add_default_arch_event(EM_HOST, ...)`; report and buildid-list add `-i <file>`.

`perf kvm stat record` builds a `perf record` invocation with raw samples, 1-sample period, 1024 mmap pages, the KVM tracepoints returned by `kvm_events_tp()`, and `-o kvm->file_name`. `perf kvm stat report` parses event, VCPU, PID, sort, force, and stdio options, initializes histograms, opens a `perf_session`, validates that the data contains KVM traces, selects architecture event ops, initializes CPU ISA decoding, processes samples, sorts histograms, and prints or browses results.

Sample handling first resolves the sample address, finds or creates the thread, obtains per-thread VCPU state on KVM entry, filters by requested VCPU and pid list, and asks architecture ops whether the sample is a begin, child, or end event. Begin events cache the timestamp and optional decoded key. End events match the active event, tolerate missing begin/end keys in some architectures, reject backward timestamps, optionally warn about long events, and update total and per-VCPU stats.

Live mode creates an evlist of host KVM tracepoints, opens and mmaps events with minimal sample bits, synthesizes threads, installs a timerfd and stdin pollfd, enables the evlist, repeatedly drains mmap buffers into ordered events, flushes by timestamp rounds, and on timer ticks sorts, prints, clears interval counters, and continues until `q` or a termination signal.

## State and Persistence Behavior

Persistent runtime state lives in `perf_kvm_stat`, global `kvm_hists`, per-thread `vcpu_event_record` objects, and allocated `kvm_event` histogram rows. Offline commands read and write perf data files only; live mode uses transient perf fds, mmap buffers, timerfd, and terminal state. Event stats are accumulated in memory and, in live mode, reset after each display interval by `clear_events_cache_stats()`.

The command mutates global perf configuration flags such as `perf_host`, `perf_guest`, `exclude_GH_default`, `use_browser`, `record_options`, and `symbol_conf` fields. Wrapper helpers allocate argv entries with `STRDUP_FAIL_EXIT()` and free them after the delegated builtin returns.

## Dependencies and Integration Points

This file integrates with perf sessions, evlists, evsels, ordered events, histograms, hpp formatting, browser UI, synthetic thread generation, target validation, symbol resolution, architecture KVM-stat hooks, KVM tracepoint descriptors, and ordinary perf builtins. Feature gates matter: most stat functionality requires `HAVE_LIBTRACEEVENT`, live mode additionally requires `HAVE_TIMERFD_SUPPORT`, and interactive browsing requires `HAVE_SLANG_SUPPORT`.

## Risks and Edge Cases

Several paths are compile-time gated, so option availability varies by build. Live mode processes copied ordered events from mmap buffers and limits events per mmap pass; regressions there can lose ordering or responsiveness. `kvm_event_expand()` reallocates per-VCPU arrays and frees the previous pointer on failure, which makes allocation failure fatal to that event state. Percentage printers use integer return types for double percentages, which can reduce comparator precision. KVM stat correctness depends heavily on architecture-specific begin/end/key hooks and tracepoint field names, especially for old kernels missing newer fields.

## Test Signals

Useful validation includes `perf kvm record/report/top/buildid-list` argv construction, stat record tracepoint selection, stat report on known KVM perf.data, VCPU and PID filtering, sort keys `sample`, `time`, `max_t`, `min_t`, `mean_t`, stdio and browser output, live mode timer refresh and `q` exit, lost-event reporting, long-duration event warnings, unsupported CPU/ISA handling, and builds with and without libtraceevent, timerfd, and slang.
