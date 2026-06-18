# sources/distributed-fs/ceph-client/kernel/bpf/stackmap.c

## Purpose
`stackmap.c` implements `BPF_MAP_TYPE_STACK_TRACE` storage and the BPF helpers that collect stack ids or raw stack data. It captures kernel or user callchains, optionally converts user instruction pointers to build-id plus file-offset records, hashes traces into a preallocated map, and exposes stack extraction/deletion operations to syscalls.

## Important APIs, Types, and Functions
`struct stack_map_bucket` stores freelist linkage, trace hash, frame count, and flexible trace data. `struct bpf_stack_map` embeds `struct bpf_map`, owns a contiguous preallocated element pool, a per-CPU freelist, bucket count, and bucket pointer table. `stack_map_alloc()` validates map attributes, allocates the bucket table, obtains perf callchain buffers, and preallocates all stack buckets. `stack_map_free()` releases the pool, freelist, map, and callchain buffers.

`stack_map_calculate_max_depth()` applies skip count and `sysctl_perf_event_max_stack`. `stack_map_get_build_id_offset()` resolves user IPs to `struct bpf_stack_build_id` entries using mmap lookup and build-id parsing, with IP fallback when lookup is unsafe. `__bpf_get_stackid()` hashes a callchain, compares or replaces buckets, and implements `BPF_F_FAST_STACK_CMP` and `BPF_F_REUSE_STACKID`. Helper front ends include `bpf_get_stackid()`, `bpf_get_stackid_pe()`, `bpf_get_stack()`, `bpf_get_stack_sleepable()`, `bpf_get_task_stack()`, `bpf_get_task_stack_sleepable()`, and `bpf_get_stack_pe()`. Syscall/map operations include `bpf_stackmap_extract()`, lookup-and-delete, get-next-key, delete, mem-usage, and map ops registration through `stack_trace_map_ops`.

## Control Flow
Map creation rejects unsupported flags, wrong key/value sizes, zero entries, oversized stack depth, and `max_entries` values that could overflow `roundup_pow_of_two()`. It rounds the hash table to a power of two, allocates `struct bpf_stack_map` plus bucket pointers, reserves global callchain buffers, then populates a freelist with fixed-size bucket objects.

For `bpf_get_stackid()`, the helper validates flags, collects a perf callchain for kernel or user frames, applies skip/max-depth logic, hashes IP data, and looks up the target bucket by `hash & (n_buckets - 1)`. A matching hash may return immediately with `BPF_F_FAST_STACK_CMP`; otherwise the helper performs full data comparison. Build-id mode allocates a candidate bucket before comparison so IPs can be translated to build-id records. On collision without `BPF_F_REUSE_STACKID`, it returns `-EEXIST`; otherwise it atomically swaps in the new bucket and returns any old bucket to the freelist.

For raw stack helpers, `__bpf_get_stack()` validates flags and element size, obtains a callchain from an input perf sample, a task stack, or `get_perf_callchain()`, copies IPs or build-id records to the caller buffer, zero-fills unused space, and clears the output buffer on validation/fault errors. Perf-event variants reuse sampled callchains when `PERF_SAMPLE_CALLCHAIN` is present and split kernel/user regions by scanning for `PERF_CONTEXT_USER`.

## State and Persistence Behavior
The map persists while its BPF map reference count is nonzero. Bucket storage is preallocated at map creation, and buckets move between the per-CPU freelist and the bucket table with atomic `xchg()`. Stack ids are not stable across replacement collisions when `BPF_F_REUSE_STACKID` is used. Build-id translation depends on the current task's `mm` and VMA state at capture time. There is no disk persistence; userspace must extract map values if it wants durable stack traces.

## Dependencies and Integration Points
The file depends on BPF map infrastructure, perf callchain APIs, stacktrace support, per-CPU freelists, build-id parsing, VMA lookup, RCU, mmap lock/unlock irq work, task stack access, BTF ids, and helper prototype registration in other BPF dispatch code. It integrates with perf-event BPF contexts, tracing helpers, syscall map operations, and userspace consumers that read stack trace map entries.

## Risks and Test Signals
Risk areas include hash collision behavior, build-id fallback correctness under mmap lock contention or missing `current->mm`, buffer clearing on errors, 32-bit stacktrace IP widening, crosstask user-stack rejection, `trace->nr` restoration in perf-event paths, and freelist exhaustion. Test signals include stack map creation flag validation, kernel/user stackid collection, build-id and raw-IP modes, fast-compare collisions, reuse vs `-EEXIST`, lookup-and-delete semantics, get-next-key iteration under RCU, sleepable stack helpers, task stack helpers, and KASAN/KCSAN stress for concurrent delete/extract/update-by-helper paths.
