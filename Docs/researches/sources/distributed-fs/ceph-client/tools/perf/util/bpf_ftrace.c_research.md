# sources/distributed-fs/ceph-client/tools/perf/util/bpf_ftrace.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_ftrace.c

Purpose: this file provides the user-space side of BPF-powered `perf ftrace latency`. It configures the `func_latency` skeleton either for a single function kprobe/kretprobe pair or for a pair of raw tracepoint events, then reads histogram buckets and summary statistics.

Important APIs and functions: `perf_ftrace__latency_prepare_bpf()` validates the target, sizes CPU/task filter and latency maps, populates rodata thresholds, loads and attaches the skeleton, and returns a dummy fd for polling. `perf_ftrace__latency_start_bpf()` and `perf_ftrace__latency_stop_bpf()` toggle the BPF `enabled` flag. `perf_ftrace__latency_read_bpf()` folds per-CPU histogram arrays and copies BPF-maintained `count`, `total`, `min`, and `max` into `struct stats`. `perf_ftrace__latency_cleanup_bpf()` destroys the skeleton.

Control flow: prepare accepts either exactly one function filter or exactly two event filters. It populates CPU filters from `user_requested_cpus` when a CPU list is supplied and task filters from the evlist thread map when a task target or no explicit target is used. Function mode attaches a kprobe and kretprobe to the same symbol; event-pair mode attaches raw tracepoint begin/end programs to the two configured event names.

State and persistence: the skeleton is a static pointer. BPF global state holds histogram buckets, aggregate totals, and min/max values for the session. The code initializes BPF `min` to `INT64_MAX` before starting. No persistent filesystem state is used.

Dependencies and integration: it depends on perf ftrace configuration structures, CPU/thread maps, stats helpers, `set_max_rlimit()`, and the generated `func_latency` skeleton. It integrates with the ftrace command's latency output by filling caller-provided bucket arrays and stats.

Risks: nested function/event invocations overwrite the per-thread timestamp in the BPF map, so recursive or reentrant targets may undercount outer latencies. The dummy `/dev/null` fd is only for poll plumbing and does not reflect BPF readiness. Static skeleton lifetime makes concurrent latency sessions in one process unsafe. Bucket accumulation does not clear `buckets[]`, so callers must provide zeroed storage.

Test signals: test single function latency and two-event latency, CPU and task filters, nanosecond and microsecond modes, bucket range/min/max options, invalid filter counts, and nested target behavior.
