# sources/distributed-fs/ceph-client/include/linux/u64_stats_sync.h

## Purpose
Provides helpers for tear-free 64-bit statistics updates on 32-bit systems while compiling to cheap/no-op paths on 64-bit systems.

## Important APIs, Types, And Functions
Defines `struct u64_stats_sync`, `u64_stats_t`, and helpers `u64_stats_read()`, `u64_stats_copy()`, `u64_stats_set()`, `u64_stats_add()`, `u64_stats_sub()`, `u64_stats_inc()`, `u64_stats_init()`, `u64_stats_update_begin/end()`, IRQ-save update variants, `u64_stats_fetch_begin()`, and `u64_stats_fetch_retry()`.

## Control Flow
Writers take their own mutual exclusion, then call update begin/end around non-atomic counter changes. On 32-bit, begin disables preemption and starts a seqcount write; end completes the seqcount and re-enables preemption. Readers loop with fetch begin/retry until they read a stable sequence. On 64-bit, seqcount operations are no-ops and counters use `local64_t`.

## State, Persistence, And Dependencies
`struct u64_stats_sync` contains a seqcount only on 32-bit. Counters are stored in `u64_stats_t`. Dependencies include seqlock and either `asm/local64.h` or string/memcpy.

## Integration Points
Used by networking and driver statistics that are updated frequently and read from procfs/sysfs/ethtool without heavy locking.

## Risks And Test Signals
Risks include missing writer mutual exclusion, failing to disable preemption on 32-bit writers, using non-IRQ variants when IRQ readers/writers exist, and assuming multiple counters are mutually consistent on 64-bit. Test signals include 32-bit stress readers, KCSAN/concurrency tests, IRQ-context stats updates, wraparound tests, and netdev stats regression coverage.
