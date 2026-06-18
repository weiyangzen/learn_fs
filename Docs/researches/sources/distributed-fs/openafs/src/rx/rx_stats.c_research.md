# sources/distributed-fs/openafs/src/rx/rx_stats.c

## Purpose
Implements allocation, copying, freeing, and reset of RX internal statistics.

## Important APIs, Types, And Functions
The file defines `rx_stats_mutex` when locks are enabled and global `struct rx_statisticsAtomic rx_stats`. Functions are `rx_GetStatistics`, `rx_FreeStatistics`, and private `rxi_ResetStatistics`.

## Control Flow
`rx_GetStatistics` allocates an external `struct rx_statistics`, locks `rx_stats_mutex`, asserts layout compatibility between atomic and external structures, copies the global stats block, unlocks, and returns it. `rx_FreeStatistics` frees a non-null stats block and clears the caller pointer. `rxi_ResetStatistics` zeroes the atomic stats structure.

## State And Persistence
Statistics are process/kernel memory counters only. No disk persistence exists. Atomic fields can be incremented without holding the stats mutex, while non-atomic fields are protected by `rx_stats_mutex` for snapshot copying.

## Dependencies And Integration Points
It depends on `rx_atomic.h`, `rx_stats.h`, RX allocation helpers `rxi_Alloc`/`rxi_Free`, and the public `struct rx_statistics` layout from RX headers. Packet, connection, and socket paths update `rx_stats`.

## Risks And Test Signals
Risks include layout drift between `rx_statisticsAtomic` and `rx_statistics`, missing locking for non-atomic members, and reset races during active traffic. Test signals are stats API calls under traffic, reset behavior, and compile-time/static assertion failures on layout changes.
