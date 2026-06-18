# sources/distributed-fs/ceph-client/samples/bpf/lathist_kern.c

Purpose: BPF kprobe sample that builds latency histograms for preemption-off sections.

Important APIs/types/functions: maps for per-CPU start timestamps and histogram slots, `log2`, `log2l`, `bpf_prog1` on `trace_preempt_off`, and `bpf_prog2` on `trace_preempt_on`.

Control flow: on preempt-off, records timestamp by CPU. On preempt-on, computes elapsed time, maps it into a log2 bucket, and increments the per-CPU histogram slot.

State and persistence: timestamps and histogram counts live in BPF maps.

Dependencies and integration: loaded by `lathist_user.c`, depends on kprobe-visible `trace_preempt_off`/`trace_preempt_on` symbols and preemption tracing support.

Risks: fixed `MAX_CPU` of 4 limits coverage. Symbol names may differ by config. Log bucket saturation can hide very high latencies.

Test signals: run under workload, observe nonzero histogram buckets per CPU, and verify attach errors on kernels without target symbols.
