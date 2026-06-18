# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.h

## Purpose

`fbnic_hw_stats.h` declares the software statistics model used by FBNIC hardware stat collection and ethtool/debugfs reporting. It defines counter wrappers, grouped hardware statistic structures, the aggregate `struct fbnic_hw_stats`, and public stats collection/reset APIs.

## Important APIs, Types, And Functions

`struct fbnic_stat_counter` is the base type: accumulated `value`, old 32-bit or 64-bit hardware snapshot, and `reported` flag. `struct fbnic_hw_stat` pairs frame and byte counters. Group structures include FEC, PCS lane symbol errors, Ethernet control stats, RMON histograms, pause stats, Ethernet MAC stats, PHY stats, MAC stats, TMI, TTI, RPC, RXB enqueue/fifo/dequeue, per-queue hardware stats, PCIe stats, and the aggregate `struct fbnic_hw_stats`.

Public functions are `fbnic_stat_rd64()`, `fbnic_reset_hw_stats()`, `fbnic_init_hw_stats()`, `fbnic_get_hw_q_stats()`, `fbnic_get_hw_stats32()`, and `fbnic_get_hw_stats()`.

## Control Flow

The header declares data and functions only. Runtime flow is implemented in `fbnic_hw_stats.c`, while ethtool and debugfs access the structures directly for reporting.

## State And Persistence

`struct fbnic_hw_stats` is embedded in `struct fbnic_dev`. Its spinlock protects most stats access. Counter values persist in memory across hardware resets because reset code refreshes baselines rather than clearing accumulated values. Some MAC-related subgroups are explicitly not updated by `fbnic_get_hw_stats()` and are fetched by MAC/ethtool-specific callbacks.

## Dependencies And Integration Points

The header depends on Linux ethtool histogram sizing, spinlocks, and CSR constants such as `FBNIC_PCS_MAX_LANES`, `FBNIC_RXB_*_INDICES`, and `FBNIC_MAX_QUEUES`. It is included through `fbnic.h` and consumed by stats implementation, ethtool, debugfs, and MAC-specific stats helpers.

## Risks And Edge Cases

Any structure layout change must be reflected in `fbnic_ethtool.c` offset tables. Array sizes are hardware-defined; changing CSR constants changes memory footprint and ethtool stats count. The `reported` flag is meaningful for MAC callbacks and must be maintained when adding counters. Locking comments for not-updated-by-`fbnic_get_hw_stats()` subgroups must remain accurate.

## Test Signals

Useful checks include compile-time struct offset users, ethtool stats count/string alignment, no out-of-bounds access for queue/RXB arrays, and locking validation around stats readers. No executable tests were run for this research item.
