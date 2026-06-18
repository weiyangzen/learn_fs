# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_data.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_data.h

Purpose: this header defines the shared data layout for lock contention BPF maps and user-space readers.

Important types and constants: `owner_tracing_data`, `tstamp_data`, `contention_key`, `contention_task_data`, `contention_data`, `slab_cache_data`, `enum lock_aggr_mode`, and `enum lock_class_sym` form the map ABI. Constants encode task comm length, max entries, high-bit pseudo-lock flags (`LCD_F_MMAP_LOCK`, `LCD_F_SIGHAND_LOCK`), slab id bit ranges, and type masks.

Control flow and state: there is no executable logic. BPF writes these structures into maps, and user space reads the same layouts to build reports.

Dependencies and integration: included by `lock_contention.bpf.c` and `bpf_lock_contention.c`; enum values must match perf lock-contention aggregation expectations.

Risks: any field reorder, size change, or flag-mask change breaks persisted map interpretation between skeleton and user-space code. The slab id range allows a finite number of cache ids and shares the `flags` field with lock type bits.

Test signals: compile BPF and user space together, run BTF/map layout checks where available, and test all aggregation modes and special-flag name decoding after changes.
