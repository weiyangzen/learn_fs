# sources/distributed-fs/ceph-client/mm/kasan/tags.c

## Purpose

`tags.c` implements shared tag-based KASAN stack tracking. It parses boot parameters for stack collection and stack-ring size, allocates the bounded stack ring, and records allocation/free stack information used later by tag-mode report classification.

## Important APIs, Types, and Functions

Key state includes `kasan_arg_stacktrace`, static key `kasan_flag_stacktrace`, `STACK_RING_BUSY_PTR`, and global `struct kasan_stack_ring stack_ring`. Boot parsers are `early_kasan_flag_stacktrace()` for `kasan.stacktrace=off|on` and `early_kasan_flag_stack_ring_size()` for `kasan.stack_ring_size=...`. Main functions are `kasan_init_tags()`, `save_stack_info()`, `kasan_save_alloc_info()`, and `kasan_save_free_info()`.

## Control Flow

Initialization applies the stacktrace boot policy, chooses the default ring size when needed, and allocates the ring from memblock. Allocation/free tracking saves a stack depot handle, takes the ring read lock, atomically advances `stack_ring.pos`, skips busy slots, claims a slot by changing `entry->ptr` to `STACK_RING_BUSY_PTR`, fills object size, track, free/alloc flag, and pointer, then releases the lock. If the slot previously referenced a stack depot handle, the old handle is dropped after publishing the new entry.

## State and Persistence Behavior

The stack ring is fixed-size runtime memory allocated at boot. It is a lossy circular history; old entries are overwritten as allocations and frees occur. The static key persists the stack-collection policy for the running kernel.

## Dependencies and Integration Points

This file integrates with slab allocation/free hooks for tag-based KASAN, stack depot, memblock, static keys, and `report_tags.c`, which walks the same ring to infer bug types and copy stack tracks. The ring lock prevents report readers from seeing partially written entries.

## Risks and Edge Cases

The busy-slot loop must avoid corrupting entries under concurrent writers. Ring size too small reduces report quality; allocation failure disables stack collection. Stack depot reference management is important because overwritten stack handles are explicitly released.

## Test Signals

Signals include boot coverage for `kasan.stacktrace` and `kasan.stack_ring_size`, tag-mode reports with alloc/free stacks, disabled-stacktrace fallback reports, and stress tests with concurrent slab allocations and frees.
