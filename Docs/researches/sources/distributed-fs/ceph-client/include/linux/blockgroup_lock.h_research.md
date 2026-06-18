# sources/distributed-fs/ceph-client/include/linux/blockgroup_lock.h

## Purpose
`blockgroup_lock.h` provides a small hashed spinlock array for per-block-group locking, originally for ext2/ext3 block group operations. It trades exact one-lock-per-group storage for a fixed number of cacheline-aligned locks.

## Important APIs, Types, And Functions
`NR_BG_LOCKS` is `1` on UP builds and `4 << ilog2(min(NR_CPUS, 32))` on SMP builds. `struct bgl_lock` wraps a `spinlock_t` and is cacheline-aligned in SMP builds. `struct blockgroup_lock` stores an array of `bgl_lock` entries. `bgl_lock_init()` initializes every lock. `bgl_lock_ptr()` selects a lock by hashing `block_group` with `block_group & (NR_BG_LOCKS - 1)`.

## Control Flow And State
The header contains only inline initialization and lookup. Persistent state is the caller-embedded `struct blockgroup_lock`. Lock selection is deterministic and lossy: multiple block groups can map to the same spinlock. The power-of-two lock count makes masking valid.

## Dependencies And Integration Points
It depends on `linux/spinlock.h` and `linux/cache.h`, and uses `NR_CPUS` and `ilog2()` from the broader kernel environment. Filesystem code uses it to protect block group metadata updates without allocating large lock arrays.

## Risks And Test Signals
Risks include lock contention when many hot groups hash to the same lock, assuming unique locks per group, missing initialization before lookup, and compile assumptions around `NR_BG_LOCKS` being a power of two. Test signals include SMP and UP builds, lockdep coverage around block group updates, hash distribution tests, and stress tests with concurrent allocation/free in adjacent block groups.
