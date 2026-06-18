# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/func_latency.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/func_latency.bpf.c

Purpose: this BPF program records latency between begin/end probes for a function or raw tracepoint pair and stores both a histogram and summary stats.

Important maps and globals: `functime` maps tid to start timestamp; `cpu_filter` and `task_filter` gate collection; `latency` is a per-CPU array histogram. BSS globals hold `enabled`, `total`, `count`, `max`, and `min`; rodata configures filters, nanosecond mode, bucket range, min/max latency fields, and bucket count.

Control flow: begin programs check `enabled` and `can_record()`, then store `bpf_ktime_get_ns()` by current pid/tgid. End programs find the timestamp, call `update_latency()`, and delete the timestamp. `update_latency()` ignores negative deltas, chooses either fixed-range or log2-style bucket indexes, increments the per-CPU bucket, updates aggregate totals, and adjusts min/max.

State and persistence: timestamps persist per current pid/tgid between begin and end events. Histogram rows and aggregate globals persist until skeleton destruction. Nested begin events for the same key overwrite previous timestamps.

Dependencies and integration: user space in `bpf_ftrace.c` attaches kprobe/kretprobe or raw tracepoint programs, sizes maps, populates filters, and reads buckets/stats.

Risks: aggregate `max` and `min` updates are not atomic, so high concurrency can race. Nested or missing end events can distort results. `max_latency` rodata is present but not used in the visible code, which may be intentional future plumbing or a stale option.

Test signals: validate bucket assignment for range and power-of-two modes, CPU/task filters, nsec/usec conversions, nested function calls, and concurrent updates on many CPUs.
