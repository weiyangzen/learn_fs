# sources/distributed-fs/ceph-client/kernel/trace/pid_list.h

## Purpose

`pid_list.h` defines the sparse PID bitmap data structure used internally by tracing. It documents the page-table-like layout that divides a PID into two 8-bit upper indexes and one 14-bit lower bitmap index, providing compact storage for sparse PID sets without allocating a full PID_MAX bitmap.

## Important APIs, Types, and Functions

- Layout constants: `UPPER_BITS`, `UPPER_MAX`, `UPPER1_SIZE`, `UPPER2_SIZE`, `LOWER_BITS`, `LOWER_MAX`, `LOWER_SIZE`, `UPPER1_SHIFT`, `UPPER2_SHIFT`, `LOWER_MASK`, `UPPER_MASK`, and `MAX_PID`.
- Cache constants: `CHUNK_ALLOC` preallocates six upper and lower chunks; `CHUNK_REALLOC` queues refill when only two chunks remain.
- `union lower_chunk` is either a free-list `next` pointer or a lower bitmap array of `LOWER_SIZE` unsigned longs.
- `union upper_chunk` is either a free-list `next` pointer or an array of `UPPER2_SIZE` lower-chunk pointers.
- `struct trace_pid_list` stores the seqcount, raw spinlock, refill irq_work, top-level upper array, free lists, and free counters.

## Control Flow

The header itself has no executable control flow, but its structure determines `pid_list.c` behavior. A PID is split by shifting and masking: the top 8 bits index `trace_pid_list.upper`, the next 8 bits index an `upper_chunk->data[]` lower-chunk pointer, and the bottom 14 bits select a bit in the lower bitmap. Empty upper/lower chunks can be moved between active tree positions and free lists because the same union memory overlays free-list linkage with active data.

## State and Persistence Behavior

State is maintained in `struct trace_pid_list` instances allocated by `trace_pid_list_alloc()`. The initial top-level array is part of the object, while upper/lower chunks are allocated separately and cached. The structure is not persistent; it is owned by a trace array or trace option and freed when the filter is cleared.

## Dependencies and Integration Points

The header assumes kernel definitions for `seqcount_raw_spinlock_t`, `raw_spinlock_t`, `irq_work`, `BITS_PER_LONG`, and PID maximum constraints from `linux/thread.h`. It is explicitly marked "Do not include this file directly", so it is intended for internal tracing headers/source files rather than general kernel users.

## Risks and Edge Cases

- The design assumes PIDs are less than `1 << 30`; larger PID namespaces would invalidate the split and are guarded by runtime warnings in the implementation.
- The union overlay requires chunks to be zeroed or fully initialized when switching from free-list to active data; stale active pointers or bits would corrupt membership.
- Memory footprint scales with sparse chunks, not PID count, but worst-case sparse PIDs across many upper indexes can allocate many 2 KiB lower bitmaps.
- Cache sizes are policy embedded in constants; changing them affects scheduler-path allocation pressure.

## Test Signals

Test signals are mostly from `pid_list.c`: correct split/join behavior at boundaries, chunk allocation/reuse, empty subtree recycling, and behavior near `MAX_PID - 1` versus `MAX_PID`. Static compile coverage should ensure structure sizes and `LOWER_SIZE` match the comments across 32-bit and 64-bit builds.
