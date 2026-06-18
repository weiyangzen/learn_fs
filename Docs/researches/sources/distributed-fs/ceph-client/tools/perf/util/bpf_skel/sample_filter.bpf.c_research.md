# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample_filter.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample_filter.bpf.c

Purpose: this BPF perf-event program interprets filter entries and decides whether a perf sample should be kept or dropped before user-space delivery.

Important maps and helpers: `filters` stores arrays of `perf_bpf_filter_entry`; `event_hash` maps event instance ids to representative ids; `idx_hash` maps event/tgid to filter index; `dropped` counts rejected samples. `perf_get_sample()` reads requested sample fields from `struct bpf_perf_event_data_kern`; `perf_sample_filter()` is the `SEC("perf_event")` entrypoint.

Control flow: the program casts the perf-event context to kernel context using `bpf_cast_to_kern_ctx`. If `use_idx_hash` is set, it resolves parent event id and current tgid to a filter index; otherwise it uses index zero. It then loops over up to `MAX_FILTERS`, evaluates each operation, supports grouped conditions by recording whether any grouped condition matched, returns 1 on `PBF_OP_DONE` or natural loop completion, and jumps to `drop` on failed non-group conditions.

State and persistence: filter maps are configured by user space and read-only from the program's perspective except for `dropped`, which is atomically incremented. No per-sample state persists.

Dependencies and integration: relies on perf's internal kernel sample structures, CO-RE field existence for `sample_flags` and data-source `mem_hops`, `sample-filter.h` enum layout, and a ksym `bpf_cast_to_kern_ctx`.

Risks: if `sample_flags` is unavailable, sample terms return zero, possibly dropping valid samples. Max/min comparisons are unsigned. Group semantics are simple "any condition in group true" and must match user-space expression generation. Kernel internal structure changes require CO-RE coverage.

Test signals: run filters on IP, TID pid/tid parts, CPU, time, period, weight, data_src parts, cgroup, page sizes, UID/GID, grouped expressions, missing idx_hash rows, and dropped-count accounting.
