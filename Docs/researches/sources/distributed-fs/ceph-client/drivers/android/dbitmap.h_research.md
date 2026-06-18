# sources/distributed-fs/ceph-client/drivers/android/dbitmap.h

## Purpose
`dbitmap.h` provides a small dynamically sized bitmap library used by Binder to allocate the smallest available descriptor ID efficiently while allowing growth and shrink decisions to be made outside locks.

## Important APIs, Types, And Functions
`struct dbitmap` stores `nbits` and `map`. Inline APIs are `dbitmap_enabled`, `dbitmap_free`, `dbitmap_shrink_nbits`, `dbitmap_replace`, `dbitmap_shrink`, `dbitmap_grow_nbits`, `dbitmap_grow`, `dbitmap_acquire_next_zero_bit`, `dbitmap_clear_bit`, and `dbitmap_init`. `NBITS_MIN` is one unsigned long worth of bits.

## Control Flow
Users initialize with `dbitmap_init`, acquire descriptor IDs with `dbitmap_acquire_next_zero_bit`, clear IDs with `dbitmap_clear_bit`, and periodically ask whether grow or shrink is needed. Grow/shrink helpers revalidate the requested size because callers may allocate replacement memory after dropping locks. If growth remains needed but allocation failed, `dbitmap_grow` disables the dynamic bitmap so Binder can fall back to a slower descriptor lookup path.

## State And Persistence
The bitmap persists as heap memory referenced by `map`. `nbits == 0` means disabled. Set bits represent allocated IDs. Shrink can reduce the allocation when the highest set bit is in the first quarter, or to `NBITS_MIN` when no bits are set.

## Dependencies
The header depends on Linux bitmap helpers and kernel allocation/free APIs. It intentionally provides no internal locking; Binder protects it with `proc->outer_lock` according to the file comment and `binder_proc` documentation.

## Integration Points
`binder_internal.h` embeds `struct dbitmap dmap` in `struct binder_proc` for reference descriptor management. Binder reference creation/removal code can use it to find free handle IDs faster than rb-tree scans.

## Risks
Callers must hold the right lock around all bitmap state access. Revalidation protects against stale out-of-lock allocation decisions, but callers must pass the exact nbits returned by `dbitmap_*_nbits`. Disabling on grow allocation failure changes performance behavior and requires fallback code to remain correct.

## Test Signals
Unit tests should cover init/free, acquire until `-ENOSPC`, clear/reacquire lowest IDs, grow with stale and valid nbits, grow allocation failure disabling, shrink thresholds, all-clear shrink to minimum, and concurrent-pattern tests under the Binder outer lock.
