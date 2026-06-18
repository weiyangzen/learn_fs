<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/trace/postprocess/trace-pagealloc-postprocess.pl -->
# sources/distributed-fs/ceph-client/Documentation/trace/postprocess/trace-pagealloc-postprocess.pl

## Purpose
Perl proof-of-concept trace postprocessor for page allocation tracepoints. It aggregates allocation/free, per-CPU page drain/refill, and external fragmentation activity by process or by process name.

## Important APIs, Types, And Functions
- Constants identify raw tracepoints, high-level derived events, and temporary state flags.
- Options: `--ignore-pid`, `--read-procstat`, and `--prepend-parent`.
- `generate_traceevent_regex()` discovers tracepoint print formats from tracefs and falls back to built-in defaults.
- `process_events()` parses stdin trace lines and updates `%perprocesspid`.
- `dump_stats()`, `aggregate_perprocesspid()`, and `report()` render per-PID or per-process summaries.
- `sigint_handler()` and `signal_loop()` allow interactive reporting without immediately terminating a live trace pipeline.

## Control Flow
The script initializes the extfrag detail regex, then loops over stdin. Each trace line is matched against a generic ftrace text regex to extract process, CPU, timestamp, tracepoint name, and details. Known page allocation tracepoints increment counters; extfrag events parse details and classify severe/moderate fragmentation. State counters detect completed per-CPU drain/refill sequences when a different tracepoint follows.

## State And Persistence
All metrics are stored in hashes keyed by `process-pid`. Optional `/proc/<pid>/stat` reads can fill missing process names or prepend parent identity. No files are written. Reports are printed at EOF or after a delayed SIGINT.

## Dependencies And Integration Points
Depends on Perl, `Getopt::Long`, Linux tracefs event format files under `/sys/kernel/tracing/events/kmem`, `/proc`, and textual ftrace streams such as `/sys/kernel/tracing/trace_pipe`.

## Risks And Edge Cases
The parser is intentionally approximate and tied to ftrace text formatting. Tracepoint format drift can cause warnings or dropped extfrag records. Several hash fields are read before initialization, which Perl treats as zero with warnings disabled by default. Parent/procstat parsing assumes process names and PIDs fit simple regexes.

## Test Signals
Use synthetic trace lines for every handled tracepoint, malformed extfrag details, missing tracefs format files, `--ignore-pid`, `--read-procstat`, and SIGINT report behavior. Counters for drains/refills should flush at EOF and on tracepoint transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/trace/postprocess/trace-pagealloc-postprocess.pl -->
