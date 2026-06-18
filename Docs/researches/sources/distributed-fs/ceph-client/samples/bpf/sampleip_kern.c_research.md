# sources/distributed-fs/ceph-client/samples/bpf/sampleip_kern.c

Purpose: BPF perf-event program that samples instruction pointers and counts occurrences.

Important APIs/types/functions: `MAX_IPS`, an IP-count map, and `SEC("perf_event") int do_sample(struct bpf_perf_event_data *ctx)`.

Control flow: on each perf sample, reads the instruction pointer from the perf event context, looks up the count in the map, initializes or increments it, and returns.

State and persistence: map stores sampled IP counts while attached.

Dependencies and integration: loaded by `sampleip_user.c`, attached to per-CPU perf events.

Risks: fixed maximum entries can drop unique IPs under broad workloads. Sampling frequency influences overhead and fidelity.

Test signals: run user sampler, wait for samples, and verify map contains kernel IPs with counts.
