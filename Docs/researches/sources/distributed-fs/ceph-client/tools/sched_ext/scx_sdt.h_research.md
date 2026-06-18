# sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.h

Purpose: shared BPF/userspace header defining the arena allocator data structures and scheduler statistics used by `scx_sdt`.

Important APIs, types, and functions: defines `struct scx_alloc_stats`, `struct sdt_pool`, `union sdt_id`, `struct sdt_desc`, `struct sdt_data`, `struct sdt_chunk`, `struct scx_allocator`, and `struct scx_stats`. Constants in `enum sdt_consts` configure a three-level tree of 512-entry chunks, bitmap word count, and minimum data elements per arena allocation. When compiled for BPF it declares allocator/task-data helpers such as `scx_task_data()`, `scx_task_init()`, `scx_task_alloc()`, `scx_task_free()`, `scx_alloc_init()`, and `scx_alloc_free_idx()`.

Control flow: this header does not execute code, but its layouts determine how `scx_sdt.bpf.c` indexes arena chunks, wraps per-task payloads behind `struct sdt_data`, stores generation-aware IDs, and presents `struct scx_stats` to both BPF and userspace skeleton readers.

State and persistence: `sdt_pool` tracks current slab, element size, capacity, and next index. `sdt_desc` persists allocation bitmaps and free counts. `sdt_data` stores the allocated index/generation ahead of the flexible payload. `scx_stats` is the per-task payload that accumulates scheduling counters until exit.

Dependencies and integration points: uses kernel fixed-width types and `pid_t`; defines `__arena` away for non-BPF compilation so userspace can include the same file. It is tightly coupled to verifier-friendly arena pointer annotations in the BPF program.

Risks: any structure layout change must preserve BPF/userspace skeleton ABI and the allocator's assumptions. `SDT_TASK_ENTS_PER_PAGE_SHIFT` and `SDT_TASK_LEVELS` set allocator capacity and bitmap sizes; changing them can break index math or verifier bounds. The header declares `scx_alloc_internal()` but the viewed BPF file implements `scx_alloc()`, so declarations should be checked against all build users.

Test signals: compile-time structure checks in the BPF source and successful skeleton generation are primary signals. Runtime signals include correct per-task stats layout in `scx_sdt.c` and allocator counters behaving consistently.
