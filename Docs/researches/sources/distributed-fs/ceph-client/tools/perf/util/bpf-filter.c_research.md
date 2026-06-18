# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.c

Purpose: implements perf's generic BPF sample filter support. It converts parsed filter expressions into BPF map entries, attaches a fixed sample-filter BPF program to perf events, supports a root-pinned shared filter setup for non-root users, and reports dropped samples.

Important APIs and functions: `perf_bpf_filter__parse()` checks capability/pinned setup and invokes the flex/bison parser. `perf_bpf_filter__prepare()` builds filter entries, validates sample flags, loads or reuses the BPF skeleton, updates maps, and attaches programs with `bpf_program__attach_perf_event_opts()` or `PERF_EVENT_IOC_SET_BPF`. `perf_bpf_filter__destroy()` frees expressions and removes pinned map entries. `perf_bpf_filter__lost_count()` reads the dropped count. `perf_bpf_filter__pin()` and `perf_bpf_filter__unpin()` manage pinned BPF objects under `/sys/fs/bpf/perf_filter`.

Control flow: parsed expressions live on `evsel->bpf_filters`. `get_filter_entries()` flattens normal expressions and one-level OR groups into `perf_bpf_filter_entry` arrays terminated by `PBF_OP_DONE`. In per-task non-root mode, `create_idx_hash()` reserves a slot in the shared `filters` map, creates event-id aliases in `event_hash`, maps `(tgid,event-id)` to the filter slot in `idx_hash`, resets dropped count, and attaches the pinned program. Root/system-wide mode loads a private skeleton and uses filter index zero.

State and persistence: `pinned_filters` tracks shared map slots to clean up later. Pinned mode persists BPF programs and maps in bpffs with relaxed permissions so non-root users can attach preloaded filters. Per-evsel private mode stores the skeleton pointer on `evsel->bpf_skel`. Filter expressions are heap allocated and freed at destroy.

Dependencies and integration points: depends on libbpf skeleton `sample_filter.skel.h`, perf evsel fd arrays, target/thread maps, capability checks, procfs for Tgid lookup, bpffs/sysfs helpers, and parser headers generated from `bpf-filter.l/.y`.

Risks: shared pinned maps have finite sizes and require cleanup; stale entries can exhaust slots or cause wrong dropped counts. `create_idx_hash()` assumes thread map pids can be converted to TGIDs via `/proc`, but threads can exit during setup. Sample flag validation must match BPF program expectations. Attaching to many event fds can partially succeed before a later failure, so cleanup paths are important. Permission and libbpf-version behavior differs between root, CAP_BPF, and non-root pinned workflows.

Test signals: parse and attach filters for system-wide and per-task targets, non-root pinned workflow, map slot exhaustion, event fd id failures, dead task pids, missing sample flags with hint output, dropped count reporting, pin/unpin permissions, and cleanup after partial attach failures.
