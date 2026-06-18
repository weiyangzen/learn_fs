# sources/distributed-fs/ceph-client/tools/perf/builtin-lock.c

## Purpose

`builtin-lock.c` implements `perf lock`, including recording lock tracepoints, reporting legacy lockdep/lock_stat sequences, printing lock metadata, delegating `script`, and reporting lock contention from either recorded `lock:contention_*` tracepoints or live BPF collection. It can aggregate by lock address, task, caller, or cgroup, filter by lock type/address/symbol/callstack/cgroup, show owner stacks, and emit stdio or CSV-style output.

## Important APIs, Types, and Functions

Global command state includes the active `perf_session`, `target`, output stream, option booleans, lock filters, injected delays, aggregation mode, RB roots for thread stats and sorted results, and the global `lockhash_table` from lock-contention utilities. `struct thread_stat` and `struct lock_seq_stat` track per-thread lock state machines for legacy lockdep events. `struct lock_stat` aggregates counts, wait times, names, flags, callstacks, and broken-state information. `struct lock_key` defines selectable sort/output fields.

Important functions include `thread_stat_findnew_*()`, `get_seq()`, legacy handlers `report_lock_acquire_event()`, `report_lock_acquired_event()`, `report_lock_contended_event()`, `report_lock_release_event()`, contention handlers `report_lock_contention_begin_event()` and `report_lock_contention_end_event()`, callchain helpers `lock_contention_caller()`, `callchain_id()`, `get_callstack()`, report orchestration `__cmd_report()`, contention orchestration `__cmd_contention()`, recorder `__cmd_record()`, filter parsers, and top-level `cmd_lock()`.

## Control Flow

`cmd_lock()` allocates and initializes the lock hash table, sets the default output to stderr, parses global options, and dispatches. `record` first checks whether legacy lock tracepoints are valid. If not, it falls back to contention tracepoints and adds a frame-pointer call graph. It then builds `perf record -R -m 1024 -c 1 --synth task` plus selected `-e` tracepoints and delegates to `cmd_record()`.

`report` uses legacy lock tracepoints. It opens perf.data, initializes symbols, installs tracepoint handlers, configures output fields and sort key, processes events, optionally combines locks with the same class name, sorts hash-table entries into a result RB tree, and prints acquired/contended/wait columns. The legacy state machine follows acquire -> contended -> acquired -> release transitions, handles read-lock nesting, updates wait time totals/min/max, and marks broken sequences when events arrive out of order.

`info` reuses the report processing path but prints thread IDs and/or lock address-to-name maps. `contention` selects aggregation mode from options, validates incompatible combinations, sets up a `lock_contention` object, and either prepares live BPF tracing or opens perf.data and installs contention tracepoint handlers. After collection or event processing it sorts by the selected contention key and prints rows according to aggregation mode. Caller aggregation hashes callchains and can save/print representative call stacks; address filters may defer symbol names until kernel maps are loaded.

## State and Persistence Behavior

Recording writes perf.data through `cmd_record()`. Reporting is in-memory: lock stats are stored in `lockhash_table`, thread state is stored in `thread_stats`, result ordering uses RB roots, and filters/delays are dynamically allocated then released by `lock_filter_finish()`. `--output` opens a file and redirects report output. BPF contention mode creates an evlist, optional workload, BPF maps/programs through `lock_contention_prepare()`, waits for a signal, reads BPF results, and cleans up.

Global state is significant and mostly process-lifetime: `trace_handler`, `sort_key`, `output_fields`, `aggr_mode`, `symbol_conf.field_sep`, and filter arrays are mutated during command parsing. `process_event_update()` reinstalls tracepoint handlers as event metadata updates arrive.

## Dependencies and Integration Points

The file depends on perf sessions, evlists, evsels, tracepoint validation, libtraceevent field access, symbol and callchain resolution, target and cgroup helpers, `util/lock-contention.h`, BPF skeleton lock data, pager and parse-options, and the ordinary `cmd_record()`/`cmd_script()` builtins. It consumes kernel tracepoints `lock:lock_acquire`, `lock:lock_acquired`, `lock:lock_contended`, `lock:lock_release`, `lock:contention_begin`, and `lock:contention_end`.

## Risks and Edge Cases

Legacy lock-stat reporting depends on CONFIG_LOCKDEP/CONFIG_LOCK_STAT tracepoints and exact event ordering; missing events produce broken sequences and skewed counts. Contention reporting has two data sources with different failure modes: perf.data requires recorded contention tracepoints, while BPF requires build support, privileges, and target validation. Caller aggregation hashes callchain IPs, so collisions are possible and unresolved callchains become unknown callers. Address and symbol filters require kernel map loading and can silently ignore unknown symbols. CSV separators are restricted because symbols and type strings use common punctuation. Some option-error paths return before freeing the lock hash table or closing output files.

## Test Signals

Useful validation includes record fallback when legacy tracepoints are absent, report on known legacy lock traces, info thread/map output, contention report from recorded contention events, BPF contention smoke tests with and without workloads, aggregation modes for caller/task/address/cgroup, lock type/address/symbol/callstack/cgroup filters, owner-stack output, CSV output and separator rejection, `--entries` limiting while footer totals remain correct, broken-sequence histograms under verbose mode, injected-delay parsing limits, and builds without BPF skeleton support.
