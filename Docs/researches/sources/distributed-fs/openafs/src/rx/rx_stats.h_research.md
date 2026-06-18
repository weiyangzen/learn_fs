# sources/distributed-fs/openafs/src/rx/rx_stats.h

## Purpose
Defines RX's internal atomic statistics structure and declares the stats globals.

## Important APIs, Types, And Functions
`struct rx_statisticsAtomic` mirrors public `struct rx_statistics` using `rx_atomic_t` for counters such as packet requests, allocation failures, socket buffer success, bogus reads, packet reads/sends by type, RTT samples, connection/peer/call counts, send failures, fatal errors, and spare counters. It declares `rx_stats_mutex`, `rx_stats`, and `rxi_ResetStatistics`.

## Control Flow
No runtime flow is present. Producers update fields directly, usually through atomic helpers; `rx_stats.c` snapshots and resets the whole structure.

## State And Persistence
The structure defines in-memory telemetry for an RX process or kernel instance. It is not persisted.

## Dependencies And Integration Points
It depends on `rx_atomic_t`, `struct clock`, and `RX_N_PACKET_TYPES`. Its layout must remain synchronized with public stats structures consumed by debug/stat APIs.

## Risks And Test Signals
Risks are ABI/layout mismatch, assuming `sizeof(rx_atomic_t) == sizeof(int)`, and inconsistent atomic versus mutex-protected access. Static assertions, stats debug queries, and counter monotonicity under load are key signals.
