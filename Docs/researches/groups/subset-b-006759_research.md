# subset-b-006759 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.c

## Purpose

`cs-etm.c` is perf's CoreSight ETM/ETE auxtrace decoder integration. It reads CoreSight metadata and AUX trace records from `perf.data`, constructs OpenCSD decoder instances, resolves trace IDs to CPU metadata, tracks thread/exception-level context, and synthesizes perf instruction and branch samples from decoded ETM packets.

## Important APIs, Types, and Functions

The central state types are `struct cs_etm_auxtrace`, `struct cs_etm_queue`, and `struct cs_etm_traceid_queue`. `cs_etm__process_auxtrace_info_full()` installs perf auxtrace callbacks and prepares metadata, queues, synthesized event attributes, timestamp conversion, trace ID mapping, and decoders. Queue and trace-id helpers include `cs_etm__setup_queue()`, `cs_etm__insert_trace_id_node()`, `cs_etm__process_aux_output_hw_id()`, `cs_etm__create_queue_decoders()`, and `cs_etm__map_trace_ids_metadata()`. Decode and synthesis functions include `cs_etm__process_timestamped_queues()`, `cs_etm__process_timeless_queues()`, `cs_etm__decode_data_block()`, `cs_etm__process_traceid_queue()`, `cs_etm__synth_instruction_sample()`, and `cs_etm__synth_branch_sample()`.

## Control Flow

Perf enters through the auxtrace-info record, builds per-CPU/per-thread queues, peeks existing AUX and AUX_OUTPUT_HW_ID records, maps trace IDs, then creates one decoder per populated queue. During event processing, AUX records are queued or dumped; ITRACE_START and SWITCH records seed thread lookup state; AUX timestamps update fallback sample time. Flush dispatches either timestamped decoding, which orders queue/channel work through `auxtrace_heap`, or timeless decoding, which drains each queue directly. Decoded packets are classified as ranges, discontinuities, exceptions, or exception returns, then converted into branch/instruction samples with appropriate flags.

## State and Persistence Behavior

Persistent input state is `perf.data` metadata, AUX trace bytes, AUX_OUTPUT_HW_ID records, event attributes, and time conversion fields. Runtime state is held in trace-id maps, packet ring buffers, branch stacks, current/previous packets, current thread references, latest kernel timestamp, and decoder offsets. The file mutates in-memory metadata trace ID fields when hardware ID records override legacy IDs, but it does not write persistent data except by optionally injecting synthesized events through the perf session pipeline.

## Dependencies and Integration Points

This file depends on OpenCSD via `cs-etm-decoder`, perf auxtrace queues/heaps, ordered events, perf sessions, maps/DSOs/symbols, thread-stack and branch sample infrastructure, CoreSight PMU metadata from Linux headers, and time conversion helpers. It integrates with `perf report`, `perf inject`, `perf script`, synthesized branch/instruction events, CoreSight raw dump mode, and DSO memory reads for instruction bytes.

## Risks and Edge Cases

Trace ID mapping is fragile when hardware IDs overlap, sink IDs change, or old metadata-only files are decoded. Timestamp handling has multiple modes: virtual timestamps, kernel timestamp fallback, user-forced timestamp use, and timeless decoding. Per-thread mode collapses trace IDs to `CS_ETM_PER_THREAD_TRACEID` and cannot support overlapping IDs. Missing DSO or kernel image data prevents instruction fetches and degrades decoding. Mixed formatted/unformatted trace in one queue is rejected. Guest/host EL mapping is intentionally approximate and supports only limited guest distinction.

## Test Signals

Useful tests include decoding old metadata-only files and newer AUX_OUTPUT_HW_ID files, per-CPU and per-thread trace captures, formatted and raw CoreSight buffers, timestamped and timeless traces, branch-only and instruction-period synthesis, missing DSO/kcore warning paths, snapshot overwrite AUX fragments, SVC/interrupt exception flag classification, and `dump_trace` raw packet output. Regression signals are stable synthesized sample counts, correct CPU/TID assignment, no trace ID mismatch errors, and ordered-event processing without stale packet samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.h

## Purpose

`cs-etm.h` defines the public constants, metadata layouts, packet structures, and exported helpers for perf's CoreSight ETM/ETE auxtrace support. It is the contract shared by `cs-etm.c`, decoder callbacks, and the auxtrace-info producer/consumer format.

## Important APIs, Types, and Functions

The header defines auxtrace-info header fields (`CS_HEADER_VERSION`, `CS_PMU_TYPE_CPUS`, `CS_ETM_SNAPSHOT`), current metadata version `CS_HEADER_CURRENT_VERSION`, ETMv3/ETMv4/ETE metadata indexes, magic values, trace-ID validation, ETMv3/ETMv4 exception numbers, `enum cs_etm_sample_type`, `enum cs_etm_isa`, `struct cs_etm_packet`, and `struct cs_etm_packet_queue`. Public functions include `cs_etm__process_auxtrace_info()`, `cs_etm_get_default_config()`, and, when OpenCSD support is enabled, queue accessors and timestamp conversion helpers.

## Control Flow

There is no executable control flow beyond inline fallbacks. The declarations let callers parse metadata blocks, identify trace architecture, validate trace IDs, interpret decoder packet state, and call into full CoreSight processing when `HAVE_CSTRACE_SUPPORT` is compiled in. Without OpenCSD, `cs_etm__process_auxtrace_info_full()` reports a clear unsupported-feature error.

## State and Persistence Behavior

The header encodes persistent `perf.data` metadata layout semantics. Version 1 introduced per-CPU parameter counts, and version 2 introduced hardware ID packet trace IDs while keeping legacy metadata fields. `struct cs_etm_packet_queue` represents transient decoder output buffering with timestamps and circular packet storage. Trace IDs are constrained to valid CoreSight ranges, with `0` reserved by perf for per-thread aggregation.

## Dependencies and Integration Points

Dependencies include `debug.h`, `util/event.h`, Linux bit helpers, perf session/PMU declarations, and OpenCSD types when available. The metadata indexes must match both perf recording code and `cs-etm.c` readers. The packet structure integrates decoder callbacks with sample synthesis and branch-stack handling.

## Risks and Edge Cases

Metadata layouts must remain append-only for versioned compatibility. Wrong parameter counts or magic values break old-file decoding. The ETMv4 and ETE index layouts intentionally overlap for common fields but diverge for `TRCDEVARCH` and timestamp-source fields. The trace ID validity macro treats invalid metadata IDs as a signal that hardware ID packets carry the real IDs.

## Test Signals

Builds should pass with and without `HAVE_CSTRACE_SUPPORT`. Compatibility tests should parse v0, v1, and v2 auxtrace-info blocks; ETMv3, ETMv4, and ETE magic values; valid and invalid trace IDs; and packet queues with discontinuity, exception, range, and empty states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data-convert-bt.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/data-convert-bt.c

## Purpose

`data-convert-bt.c` implements `perf data convert --to-ctf` using Babeltrace CTF writer APIs. It opens a perf session, maps perf sample and selected non-sample records into CTF event classes and streams, writes environment and clock metadata, and flushes per-CPU streams.

## Important APIs, Types, and Functions

Key types are `struct ctf_writer`, `struct ctf_stream`, `struct convert`, and `struct evsel_priv`. Public entry `bt_convert__perf2ctf()` configures the perf tool callbacks and drives conversion. Field creation and population are handled by `value_set*()`, `string_set_value()`, `add_generic_types()`, `add_generic_values()`, `add_tracepoint_types()`, `add_tracepoint_values()`, `add_bpf_output_types()`, and `add_callchain_output_values()`. Writer setup/teardown lives in `ctf_writer__init()`, `ctf_writer__setup_clock()`, `ctf_writer__setup_env()`, `setup_streams()`, and `ctf_writer__cleanup()`.

## Control Flow

Conversion initializes a `perf_data` reader, creates a `perf_session`, parses optional time ranges, initializes the CTF writer and common integer/string field types, registers event classes from the session's evsels, optionally registers comm/fork/exit/mmap non-sample classes, then processes ordered events. Sample callbacks skip samples outside requested time ranges, create a CTF event from the evsel-private class, add generic sample fields, tracepoint fields, callchain data, and BPF raw output, append to a CPU stream, and flush streams every `STREAM_FLUSH_COUNT` events or at the end.

## State and Persistence Behavior

Persistent output is a CTF trace directory at the requested path. Runtime state includes event counters, skipped counts, stream objects indexed by CPU, CTF field type objects, event-class pointers attached to `evsel->priv`, and optional time-range filters. Input state is read-only `perf.data`; the converter does not mutate captured records.

## Dependencies and Integration Points

The file depends on Babeltrace CTF writer/IR APIs, perf sessions/tools/evlists, libtraceevent for tracepoint metadata, perf time utilities, clock metadata, and perf config for `convert.queue-size`. It integrates with perf's ordered event processing, tracepoint format parsing, BPF output events, callchain resolution, and non-sample event processors.

## Risks and Edge Cases

Identifier collisions and CTF reserved words are handled by aliases, but duplicate names only allow `_dupl_1` through `_dupl_9`. Unsupported sample fields are explicitly omitted, including read, branch stack, user regs, and user stack. Dynamic tracepoint fields require correct offset/length interpretation. CPU values beyond stream capacity are forced to stream 0 after an error. Pipe-mode feature ordering requires delayed event class setup. Error paths must release Babeltrace references to avoid leaks.

## Test Signals

Tests should cover normal samples, tracepoint samples with common and dynamic fields, BPF output, callchains, `--all` non-sample export, pipe-mode feature events, time filtering, TOD clock conversion requiring clock metadata, queue-size config, high CPU ids, unprintable strings, and CTF readability by Babeltrace tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data-convert-bt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data-convert-json.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/data-convert-json.c

## Purpose

`data-convert-json.c` implements perf data conversion to a JSON document. It writes perf header metadata and sample records with timestamp, PID/TID, CPU, comm, callchain entries, symbols/DSOs, and tracepoint raw fields when libtraceevent is available.

## Important APIs, Types, and Functions

The main runtime type is `struct convert_json`, carrying `perf_tool`, output stream, first-item delimiter state, time ranges, and counters. `bt_convert__perf2json()` is the public entry. JSON helpers include `output_json_string()`, `output_json_delimiters()`, `output_json_format()`, and key/value wrappers. `process_sample_event()` resolves samples and emits sample JSON objects, while `output_headers()` emits file and environment metadata.

## Control Flow

The converter rejects currently unsupported `--all` and `--tod`, opens the output with `O_EXCL` unless forced, creates a perf session, initializes symbols, parses optional time ranges, writes a top-level object with version and headers, processes ordered events through perf callbacks, appends sample objects into a JSON array, then closes the document and reports counts. Samples are skipped if outside the requested time range and otherwise resolved through `machine__resolve()`.

## State and Persistence Behavior

Persistent output is a single JSON file. The output is streamed directly through `FILE *out`; `first` controls comma placement. It reads `perf.data` without modification and relies on symbol resolution state initialized from the session environment. The JSON version field is `linux-perf-json-version: 1` for future compatibility.

## Dependencies and Integration Points

The file integrates with `perf_session__process_events()`, symbol initialization, machine/thread/map resolution, callchain context markers, perf header/environment metadata, auxtrace pass-through processors, and libtraceevent field formatting. It shares `struct perf_data_convert_opts` with the CTF converter but supports fewer options.

## Risks and Edge Cases

JSON escaping must preserve valid RFC 8259 output for quotes, backslashes, and control characters. If sample resolution fails, conversion errors. Context marker handling must track kernel/user/hypervisor mode across callchain entries. Tracepoint raw fields are printed as strings from libtraceevent rather than typed JSON values. Error handling after `perf_session__new()` assumes `session` is valid on later labels, so early setup changes should be careful.

## Test Signals

Tests should validate syntactically valid JSON, force/no-force output behavior, time filtering and skipped counts, samples with and without callchains, symbol and DSO emission, CPU fallback from thread state, tracepoint raw field output with libtraceevent, auxtrace-containing perf data, and unsupported-option error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data-convert-json.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data-convert.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/data-convert.h

## Purpose

`data-convert.h` declares the shared option structure and converter entry points used by perf data conversion commands.

## Important APIs, Types, and Functions

`struct perf_data_convert_opts` contains `force`, `all`, `tod`, and optional `time_str`. `bt_convert__perf2ctf()` is declared only when Babeltrace support is compiled in. `bt_convert__perf2json()` is always declared.

## Control Flow

The header has no control flow. It lets command code select a converter and pass the same option bundle to either CTF or JSON conversion. Conditional compilation hides the CTF entry when the dependency is unavailable.

## State and Persistence Behavior

The header stores no state. Its option fields influence persistent outputs: overwrite behavior, whether non-sample events are exported, wall-clock timestamp conversion for CTF, and time-range filtering.

## Dependencies and Integration Points

It depends only on `<stdbool.h>` and integrates command-line parsing with `data-convert-bt.c` and `data-convert-json.c`.

## Risks and Edge Cases

Callers must honor compile-time availability of `bt_convert__perf2ctf()`. Not every option is supported by every backend; JSON rejects `all` and `tod`, while CTF supports both subject to metadata availability.

## Test Signals

Build tests should cover configurations with and without `HAVE_LIBBABELTRACE_SUPPORT`. CLI tests should confirm option forwarding, JSON unsupported-option errors, CTF TOD clock metadata validation, and force overwrite behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data-convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/data.c

## Purpose

`data.c` implements perf's `perf_data` file abstraction for reading and writing `perf.data` as a regular file, pipe, or directory layout. It handles opening, closing, directory member files, backup rotation, read/write/seek wrappers, output switching, kcore side paths, and perf magic detection.

## Important APIs, Types, and Functions

Public APIs include `perf_data__open()`, `perf_data__close()`, `perf_data__read()`, `perf_data__write()`, `perf_data__seek()`, `perf_data_file__write()`, `perf_data_file__seek()`, `perf_data__switch()`, `perf_data__create_dir()`, `perf_data__open_dir()`, `perf_data__close_dir()`, `perf_data__size()`, `perf_data__make_kcore_dir()`, `perf_data__kallsyms_name()`, `perf_data__guest_kallsyms_name()`, `has_kcore_dir()`, and `is_perf_data()`.

## Control Flow

Opening first detects stdin/stdout pipe use, defaults a missing path to `perf.data`, rotates an existing writable file to `.old`, detects directory inputs in read mode, then opens either the directory header file or a single regular file. Directory creation builds `data.N` files and raises `RLIMIT_NOFILE` on `EMFILE`. Directory opening scans regular `data.*` members. Read/write/seek dispatch through stdio for pipes or file-descriptor helpers for regular files. Switching renames current output and optionally reopens the original path at a requested position.

## State and Persistence Behavior

Persistent effects include creating/truncating perf data files, creating perf data directories, rotating existing output to `.old`, deleting old backups via `rm_rf_perf_data()`, creating `kcore_dir`, and renaming switched outputs. Runtime state is stored in `struct perf_data` and nested `perf_data_file` descriptors, file sizes, directory version, and directory file arrays.

## Dependencies and Integration Points

The file depends on POSIX file APIs, perf header magic checks, resource-limit helpers, debug printing, `rm_rf_perf_data()`, and `readn`/`writen`. It is used broadly by perf record, report, inject, archive, data convert, and auxtrace readers through `perf_data__fd()`.

## Risks and Edge Cases

Pipe detection must not accidentally close standard streams incorrectly. Directory layouts require a `DIR_FORMAT` version and at least one `data.*` file. Existing output rotation can fail on unknown files in `.old`. Ownership checks reject files not owned by root or the effective user unless forced. `has_kcore_dir()` uses prefix matching for `kcore_dir`, so callers should not treat it as an exact path validator. Output switching returns a file descriptor even after rename warnings, so callers must inspect errors carefully.

## Test Signals

Tests should cover read/write regular files, stdin/stdout pipes, empty file rejection, ownership force behavior, output backup rotation, directory create/open/size/close, `RLIMIT_NOFILE` retry behavior, output switching with `at_exit` true and false, kcore kallsyms path discovery, guest kallsyms path discovery, and magic detection on valid and invalid files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/data.h

## Purpose

`data.h` declares the `perf_data` abstraction used to access perf data streams, files, and directory-backed captures.

## Important APIs, Types, and Functions

`enum perf_data_mode` selects read or write. `enum perf_dir_version` distinguishes single-file and directory formats. `struct perf_data_file` wraps a path plus either fd or `FILE *`, size, and stdio mode. `struct perf_data` stores top-level path, backing file, pipe/dir/force/update flags, mode, and directory member files. Inline helpers expose fd, mode, pipe/dir/single-file status. The header declares open/close/read/write/seek/switch, directory, size, kcore, kallsyms, and magic-check helpers.

## Control Flow

The header only provides inline dispatchers. `perf_data_file__fd()` selects `fileno(fptr)` for stdio-backed pipes or the raw fd otherwise. Mode and layout predicates guide implementation and callers.

## State and Persistence Behavior

The structures are mutable runtime state representing open descriptors, file sizes, directory contents, and user-requested behavior. Persistent filesystem changes are performed by `data.c`, not this header.

## Dependencies and Integration Points

Dependencies are standard I/O, booleans, unistd, and Linux integer types. The API is consumed by most perf commands and by auxtrace/data-conversion code that needs file descriptors and seek/read/write wrappers.

## Risks and Edge Cases

Callers must initialize mode and path/flags consistently before opening. `perf_data__fd()` assumes an open file. Directory state must be closed with `perf_data__close_dir()` or `perf_data__close()`. `perf_data__is_single_file()` is based on directory version, so version initialization matters for directory captures.

## Test Signals

Compile tests should catch ABI changes. Runtime tests should verify inline helpers against pipe, regular file, and directory objects; stdio-backed pipes; in-place update opens; and directory version transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/db-export.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/db-export.c

## Purpose

`db-export.c` provides a generic export layer that assigns stable numeric database IDs to perf entities and invokes backend callbacks suitable for SQL or other database importers. It exports evsels, machines, threads, comms, DSOs, symbols, samples, call paths, call returns, branch types, and context switches.

## Important APIs, Types, and Functions

Initialization and teardown are `db_export__init()` and `db_export__exit()`. Entity exporters include `db_export__evsel()`, `db_export__machine()`, `db_export__thread()`, `db_export__comm()`, `db_export__exec_comm()`, `db_export__comm_thread()`, `db_export__dso()`, `db_export__symbol()`, `db_export__sample()`, `db_export__branch_types()`, `db_export__call_path()`, `db_export__call_return()`, and `db_export__switch()`. Internal helpers resolve DB ids from `addr_location`, build call paths from callchains, and map PID/TID pairs to known threads/comms.

## Control Flow

Each entity exporter first checks whether the object already has a DB id, assigns the next per-entity counter if not, then calls the backend callback when present. Sample export ensures evsel, machine, main thread, thread, exec comm, current comm, DSO, symbol, optional call path, and optional branch target IDs are available before invoking `export_sample`. Context-switch export resolves outgoing and incoming threads from normal or CPU-wide switch records, filters untraced/idle-only switches, then calls `export_context_switch`.

## State and Persistence Behavior

Runtime state lives in `struct db_export`: callback pointers, optional call-return processor and call-path root, and monotonic last-id counters. The code mutates perf objects by setting `db_id` fields on evsels, machines, threads, comms, DSOs, symbols, call paths, and call returns. Persistence is delegated entirely to backend callbacks.

## Dependencies and Integration Points

The module depends on perf machine/thread/comm/DSO/symbol/map/event/callchain/thread-stack/call-path infrastructure. It is intended for tools such as `perf script` database exports that provide backend-specific callbacks. Branch type names align with perf IP flag combinations generated by sampling and auxtrace code.

## Risks and Edge Cases

Export ordering matters because relational backends need referenced rows before samples. Missing maps or machines cause sample export failure. Unknown symbols are synthesized and inserted into DSOs to keep references non-null. `callchain_param.order` is temporarily changed and must always be restored. Main-thread and exec-comm relationships are subtle around `exec()` because comm identity can change without PID changes. Context switches involving only unknown or idle threads are intentionally skipped.

## Test Signals

Tests should assert ID monotonicity and no duplicate backend calls, complete dependency ordering for sample exports, unknown-symbol insertion, callchain-to-call-path creation, branch-type table emission including trace-begin/end variants, context-switch in/out and preempt flags, main-thread exec comm relationships, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/db-export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/db-export.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/db-export.h

## Purpose

`db-export.h` declares the database export interface used by perf export backends. It defines the callback table, ID counters, and sample-export payload structure.

## Important APIs, Types, and Functions

`struct export_sample` packages the raw event, sample, evsel, address location, assigned sample ID, related comm/DSO/symbol IDs, offsets, branch target IDs, and call path ID. `struct db_export` holds callback pointers for each exportable entity plus state for call-return/call-path processing and last assigned IDs. The header declares all `db_export__*` entity, sample, branch, call, and switch helpers.

## Control Flow

The header has no executable flow. It defines the backend contract: callers initialize `db_export`, fill callback pointers, then call helper functions while processing perf events. Helpers in `db-export.c` enforce ID assignment and callback order.

## State and Persistence Behavior

`struct db_export` is mutable session state. Its counters persist only for the export run, while callback implementations decide whether and how rows are persisted.

## Dependencies and Integration Points

The header depends on Linux integer and list types and forward declarations for perf event/session entities. It integrates perf's internal object model with external database writers without exposing backend-specific schema code.

## Risks and Edge Cases

Callback implementers must tolerate optional IDs being zero when data is unavailable. The call-return and context-switch callbacks are only meaningful when the corresponding processor/root state is configured. The header references `struct symbol` without a forward declaration in this file, relying on include order or indirect declarations in consumers.

## Test Signals

Compile tests should cover independent include usage by export backends. Runtime backend tests should validate all callbacks receive stable IDs, zero optional IDs are handled, and context-switch/sample/call-return schemas match the populated fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/db-export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debug.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/debug.c

## Purpose

`debug.c` implements perf's general debug, verbose, quiet, trace-dump, and stack-dump support. It centralizes debug output routing, optional timestamps, raw event dumping, sublevel debug-option parsing, libapi print hooks, and backtrace reporting.

## Important APIs, Types, and Functions

Global controls include `verbose`, `quiet`, `dump_trace`, `debug_ordered_events`, `debug_data_convert`, `debug_peo_args`, `debug_kmaps`, and `debug_type_profile`. Public functions include `debug_file()`, `debug_set_file()`, `debug_set_display_time()`, `veprintf()`, `eprintf()`, `eprintf_time()`, `pr_stat()`, `dump_printf()`, `trace_event()`, `perf_debug_option()`, `perf_quiet_option()`, `perf_debug_setup()`, `__dump_stack()`, `dump_stack()`, and `sighandler_dump_stack()`.

## Control Flow

`veprintf()` emits only when the selected variable meets the requested level, routing to UI helpline or the debug file. Time-prefixed helpers print wall-clock or perf timestamp prefixes. `trace_event()` dumps raw binary event bytes only when `dump_trace` is set. `perf_debug_option()` parses comma/sublevel options and adjusts libtraceevent log level. Quiet mode sets all debug values to disabled. Stack dumping builds a live machine/thread model when possible, resolves each frame to symbol/source, and falls back to `backtrace_symbols_fd()` if available.

## State and Persistence Behavior

State is process-global and not persisted across perf runs. `_debug_file` defaults lazily to stderr with a warning if not configured. Signal handling prints a stack, restores the default handler, and re-raises the signal.

## Dependencies and Integration Points

The module integrates with perf UI, color output, binary printers, event and symbol resolution, source-line lookup, libtraceevent logging, libapi debug hooks, and optional execinfo backtrace support. `debug.h` macros route most perf diagnostics here.

## Risks and Edge Cases

Stack dumping from a signal handler uses non-async-safe operations by design and documents that risk. Debug routing changes under browser UI unless `debug=stderr` is requested. Quiet mode must reset bool-like debug globals to zero after setting sublevel values to `-1`. Lazy debug-file initialization can recurse through warning macros if changed carelessly.

## Test Signals

Tests should cover verbose thresholds, debug suboptions, quiet mode suppression, timestamp display, stderr override with browser UI, raw event dump formatting, libtraceevent log-level adjustment, stack dumping with and without backtrace support, and signal handler re-raise behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debug.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/debug.h

## Purpose

`debug.h` declares perf's debug-printing API and common diagnostic macros used across the perf utility code.

## Important APIs, Types, and Functions

The header declares global debug controls, `pr_err`, `pr_warning`, `pr_warning_once`, `pr_info`, `pr_debug`, `pr_debugN`, `pr_debug2_peo`, timestamped ordered-event macros, UI warning/error functions, `dump_printf()`, `trace_event()`, `pr_stat()`, `eprintf*()`, debug option helpers, debug-file setters, stack dump helpers, and `STRERR_BUFSIZE`.

## Control Flow

Most behavior is macro expansion into `eprintf()` or `eprintf_time()`, with one-shot warnings implemented through function-local static flags. `pr_debug2_peo` uses `debug_peo_args` to force perf-event-open traces at level 0 or normal debug level 2.

## State and Persistence Behavior

The header exposes process-global debug variables owned by `debug.c`. One-shot warning macros create static state at each call site. No persistent state is written.

## Dependencies and Integration Points

It depends on stdarg/stdbool/stdio and Linux compiler annotations. It is included throughout perf and forms the stable interface between local modules and `debug.c`.

## Risks and Edge Cases

Macros evaluate formatting arguments only when called into functions, but callers must still avoid side effects in macro arguments where normal C evaluation applies. Call-site static state in `*_once` macros is per expansion. Debug global semantics mix integer levels and bool-like flags, so quiet/setup code must handle both.

## Test Signals

Build tests should validate printf-format checking. Runtime tests should verify once-only warnings, ordered-event timestamp macros, perf-event-open debug routing, UI warning macros, and quiet/verbose interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.c

## Purpose

`debuginfo.c` wraps elfutils DWARF/DWFL access for perf. It opens distro or build-id debuginfo files, falls back to the original binary under symfs, exposes text-section offset lookup, and optionally retrieves source files from debuginfod.

## Important APIs, Types, and Functions

`debuginfo__new()` is the public constructor. It uses `dso__read_binary_type_filename()` across Fedora, Ubuntu, OpenEmbedded, build-id, and mixed-up Ubuntu debuginfo locations before falling back to the given path. `__debuginfo__new()` and `debuginfo__init_offline_dwarf()` allocate and initialize DWFL/DWARF state. `debuginfo__delete()` releases it. `debuginfo__get_text_offset()` finds relocation `.text` section offsets. `get_source_from_debuginfod()` wraps `debuginfod_find_source()` when enabled.

## Control Flow

The constructor creates a temporary DSO for the path, reads its build ID if available, tries known debuginfo binary types in order, releases the DSO, and opens the symfs-joined original binary if no separate debuginfo succeeds. DWFL initialization reports an offline module, obtains DWARF and build-id data, then finalizes reporting. Text offset lookup scans DWFL relocation entries for `.text` and reads its ELF section header.

## State and Persistence Behavior

Runtime state is `struct debuginfo` with DWARF handle, DWFL module/session, relocation bias, and build ID pointer. `debuginfo_path` is a static callback variable for standard debuginfo lookup. Debuginfod may create local cache entries through elfutils behavior, but this file only receives and returns a fetched path.

## Dependencies and Integration Points

It depends on elfutils DWARF/DWFL/GELF APIs, perf DSO/build-id/symbol helpers, symfs path joining, debug logging, and optional debuginfod. It supports source-line, probe, annotation, and symbol consumers that need DWARF data.

## Risks and Edge Cases

Open failures collapse to `-ENOENT`, losing some detailed diagnostics. The FD passed to `dwfl_report_offline()` is owned by DWFL on success but must be closed on early failure when DWFL was not created. `debuginfo__get_text_offset()` returns success even if `.text` was not found after scanning, so callers need to validate output initialization. Debuginfod build ID length is passed as zero, relying on elfutils interpretation of the string argument.

## Test Signals

Tests should cover separate distro debuginfo discovery, build-id lookup, fallback binary opening, invalid ELF files, symfs paths, kernel module `.text` offset with and without adjustment, debuginfod success/failure, and builds without debuginfod support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.h

## Purpose

`debuginfo.h` declares perf's DWARF debuginfo wrapper and provides no-op fallback definitions when libdw or debuginfod support is unavailable.

## Important APIs, Types, and Functions

With `HAVE_LIBDW_SUPPORT`, `struct debuginfo` contains `Dwarf *`, `Dwfl_Module *`, `Dwfl *`, bias, and build ID. It declares `debuginfo__new()`, `debuginfo__delete()`, and `debuginfo__get_text_offset()`. Without libdw, the same APIs are inline stubs returning `NULL` or `-EINVAL`. `get_source_from_debuginfod()` is declared or stubbed depending on `HAVE_DEBUGINFOD_SUPPORT`.

## Control Flow

The header chooses real or stub APIs at compile time. Stub paths avoid linking DWARF/debuginfod code while allowing callers to compile with graceful failure handling.

## State and Persistence Behavior

Real state is allocated in `debuginfo.c`; stub state is an empty struct. Debuginfod output path allocation is available only with support enabled.

## Dependencies and Integration Points

It depends on errno values and Linux compiler annotations. With libdw, it includes `dwarf-aux.h`. It integrates symbol/source/probe code with optional DWARF availability.

## Risks and Edge Cases

Callers must check for `NULL` debuginfo and negative offsets because unsupported builds compile successfully but do not provide functionality. The stub typedef `Dwarf_Addr` as `void` can expose misuse if callers assume arithmetic in unsupported builds.

## Test Signals

Build matrix tests should include libdw on/off and debuginfod on/off. Runtime tests should confirm unsupported builds return `-EINVAL` or `-ENOTSUP` and supported builds open real DWARF and source lookup data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.cpp -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.cpp

## Purpose

`demangle-cxx.cpp` provides perf's C++ symbol demangling wrapper with multiple backend choices.

## Important APIs, Types, and Functions

The single exported function is `cxx_demangle_sym(const char *str, bool params, bool modifiers)`. Depending on build configuration it calls `bfd_demangle()`, `cplus_demangle()`, or `abi::__cxa_demangle()`. `DMGL_PARAMS` and `DMGL_ANSI` are defined when needed to control argument and modifier inclusion.

## Control Flow

The function selects the first available compile-time backend. BFD and cplus-demangle paths honor `params` and `modifiers`; the `__cxa_demangle` path ignores those flags and returns the ABI demangler result. If no backend is compiled in, it returns `NULL`.

## State and Persistence Behavior

No state is stored. Returned demangled strings are heap allocated by the backend and must be freed by the caller according to perf's demangler contract.

## Dependencies and Integration Points

It depends on `demangle-cxx.h`, optional BFD, optional libiberty cplus demangle support, optional C++ ABI demangle support, and C linkage for consumption by C perf code. It integrates with symbol display and reporting paths.

## Risks and Edge Cases

Backend semantics differ: `__cxa_demangle` may include full parameter/modifier information regardless of requested flags, while BFD/libiberty honor flags. Invalid or non-C++ names return `NULL`. Build-system macro order determines which backend is used.

## Test Signals

Tests should cover mangled C++ names with and without parameter/modifier requests, invalid names, all supported backend configurations, no-backend builds, and caller freeing behavior under leak sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.h

## Purpose

`demangle-cxx.h` declares the C-compatible interface for C++ symbol demangling.

## Important APIs, Types, and Functions

It declares `char *cxx_demangle_sym(const char *str, bool params, bool modifiers);` and wraps the declaration in `extern "C"` when included from C++.

## Control Flow

There is no runtime flow. The C++ guard ensures that the implementation can be compiled as C++ while perf's C code can link to an unmangled symbol.

## State and Persistence Behavior

No state is stored. The returned pointer ownership belongs to the caller.

## Dependencies and Integration Points

It depends on `<stdbool.h>` and integrates symbol formatting code with `demangle-cxx.cpp`.

## Risks and Edge Cases

Callers must handle `NULL` when no backend exists or demangling fails. Because output allocation is backend-owned, callers should use the expected free routine rather than stack storage assumptions.

## Test Signals

Build tests should include C and C++ translation units including this header. Runtime tests should verify flags are forwarded and `NULL` is accepted by display paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.c

## Purpose

`demangle-java.c` demangles OpenJDK-style Java method descriptors into human-readable return type, class, method, and argument strings for perf symbol display.

## Important APIs, Types, and Functions

The exported API is `java_demangle_sym(const char *str, int flags)`. The internal parser `__demangle_java_sym()` walks descriptor text in modes `MODE_PREFIX`, `MODE_CLASS`, `MODE_FUNC`, `MODE_TYPE`, and `MODE_CTYPE`. `base_types` maps Java descriptor letters to type names. `JAVA_DEMANGLE_NORET` suppresses return-type output.

## Control Flow

`java_demangle_sym()` finds the closing `)` separating arguments from return type, allocates a buffer with an estimated expansion factor, optionally demangles the return type first, then demangles the class/function/argument prefix. The parser handles object descriptors starting with `L`, package separators `/`, arrays `[`, primitive descriptors, void, argument delimiters, and class terminators `;`.

## State and Persistence Behavior

No persistent state exists. The demangled string is heap allocated and owned by the caller. Parser state is local: output length, array depth, argument count, and mode.

## Dependencies and Integration Points

It depends on perf string formatting (`scnprintf`), Linux ctype/kernel helpers, and `demangle-java.h`. It integrates with symbol display paths for Java/JIT symbol names.

## Risks and Edge Cases

Malformed descriptors return `NULL`. The parser is intentionally OpenJDK-focused and not GCJ-compatible. Buffer truncation can stop output early if the expansion estimate is insufficient. Array state must be reset after each type. Object class parsing depends on descriptor grammar and can reject unusual or partial names.

## Test Signals

Tests should cover primitive returns, object returns, void, arrays of primitives and objects, multiple arguments, nested package names, `JAVA_DEMANGLE_NORET`, malformed missing parentheses, bad array placement, truncated/partial descriptors, and null input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.h

## Purpose

`demangle-java.h` declares perf's Java symbol demangling function and option flag.

## Important APIs, Types, and Functions

It defines `JAVA_DEMANGLE_NORET` and declares `char *java_demangle_sym(const char *str, int flags);`.

## Control Flow

There is no control flow. Consumers include the header and request Java descriptor demangling with or without return types.

## State and Persistence Behavior

No state is stored. Returned strings are heap allocated by `demangle-java.c` and owned by the caller.

## Dependencies and Integration Points

The header has no external dependencies beyond C compilation. It integrates perf's symbol formatting logic with the Java parser.

## Risks and Edge Cases

Callers must accept `NULL` for non-Java or malformed names. The flag space currently contains only `JAVA_DEMANGLE_NORET`, so future flags should avoid changing existing behavior.

## Test Signals

Tests should compile consumers, verify flag handling, and ensure display paths fall back gracefully when demangling returns `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.c

## Purpose

`demangle-ocaml.c` demangles OCaml native-code symbols emitted with the `caml` prefix into more readable module/function names.

## Important APIs, Types, and Functions

The exported API is `ocaml_demangle_sym(const char *sym)`. `ocaml_is_mangled()` recognizes names beginning with `caml` followed by an uppercase letter. The demangler rewrites `__` to `.`, decodes `$xx` hex escapes, and otherwise copies characters after the prefix.

## Control Flow

The function first rejects symbols that do not match the OCaml mangling shape. For matching symbols, it allocates an output buffer no larger than the input, skips the `caml` prefix, then scans until the end applying the two rewrite rules and null-terminating the result.

## State and Persistence Behavior

There is no global or persistent state. Returned strings are heap allocated and caller-owned.

## Dependencies and Integration Points

It depends on `util/string2.h` for hex decoding, Linux ctype helpers, and `demangle-ocaml.h`. It integrates with perf symbol display where language-specific demanglers are attempted.

## Risks and Edge Cases

The scanner checks `sym[i + 1]` and `sym[i + 2]` for escape patterns, so malformed trailing `_` or `$` near the string end relies on the NUL terminator being safe to inspect. The recognizer intentionally excludes lowercase-after-prefix symbols. Hex escapes can decode to non-printable bytes.

## Test Signals

Tests should cover valid module/function symbols, double-underscore module separators, `$xx` escapes, lowercase or missing-prefix rejection, trailing `$` and partial hex sequences, allocation failure behavior, and display fallback on `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.h

## Purpose

`demangle-ocaml.h` declares perf's OCaml symbol demangling interface.

## Important APIs, Types, and Functions

It declares `char *ocaml_demangle_sym(const char *str);`.

## Control Flow

There is no executable flow. Consumers call the function and use `NULL` as the signal that a symbol was not OCaml-mangled or could not be demangled.

## State and Persistence Behavior

No state is stored. Returned strings are heap allocated and caller-owned.

## Dependencies and Integration Points

The header has no external dependencies and integrates symbol display code with `demangle-ocaml.c`.

## Risks and Edge Cases

Callers must handle `NULL` and free non-null results. The API does not expose flags, so all behavior changes in the implementation affect all consumers.

## Test Signals

Compile tests should cover inclusion from C files. Runtime tests should verify non-OCaml fallback, allocation ownership, and formatted symbol output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.h -->
