# sources/distributed-fs/ceph-client/lib/bucket_locks.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bucket_locks.c` allocates arrays of spinlocks sized for hash-bucket style locking. It centralizes lock-array sizing, initialization, and lockdep class assignment for subsystems that shard locking by hash.

## Important APIs, Types, and Functions

The exported functions are `__alloc_bucket_spinlocks()` and `free_bucket_spinlocks()`. Inputs include output lock pointer, output mask, maximum size, locks-per-CPU multiplier, GFP flags, lockdep name, and lock class key.

## Control Flow

Allocation chooses a size from either `max_size` or `min(num_possible_cpus() * cpu_mult, max_size)`, with `CONFIG_PROVE_LOCKING` forcing a smaller pseudo-CPU count. It allocates with `kvmalloc_objs()`, initializes each spinlock, assigns the lockdep map, stores `size - 1` as the mask, and returns zero or `-ENOMEM`. Freeing delegates to `kvfree()`.

## State and Persistence Behavior

The only persistent state is the caller-owned lock array and mask. The file does not track allocations globally. Lock instances persist until `free_bucket_spinlocks()` is called.

## Dependencies and Integration Points

Dependencies are spinlock APIs, lockdep, CPU count helpers, `kvmalloc_objs`, and `kvfree`. Integration points are hash tables and caches that index locks by `hash & locks_mask`; callers are expected to request power-of-two-compatible sizing.

## Risks and Edge Cases

The function stores `size - 1` as a mask, so a non-power-of-two `max_size` can produce an invalid hash mask despite the comment saying the size is rounded. A zero size would underflow the mask. `sizeof(spinlock_t) == 0` paths keep `locks` NULL but still return a mask.

## Test Signals

Tests should verify allocation success/failure, lockdep class initialization, CPU multiplier sizing, mask correctness for caller-supplied power-of-two sizes, zero and non-power-of-two guard behavior in callers, and clean `kvfree()` teardown.

## Read Coverage

Source read size: 54 lines, 1428 bytes.
