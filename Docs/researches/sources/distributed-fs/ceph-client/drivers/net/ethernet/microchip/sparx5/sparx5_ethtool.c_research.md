# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ethtool.c

## Purpose
This file provides Sparx5 ethtool operations and the driver statistics subsystem. It periodically extends hardware 32-bit counters into 64-bit software counters, exposes standard IEEE/RMON stats, exposes custom stats strings/data, delegates link and pause settings to phylink, and reports PTP timestamping capabilities.

## Important APIs, Types, And Functions
Exports are `sparx5_ethtool_ops`, `sparx5_stats_init()`, `sparx5_stats_deinit()`, and `sparx5_get_stats64()`. Important internals include `sparx5_update_counter()`, device/ASM counter readers, XQS queue-stat readers, ANA_AC policer-stat readers, ethtool standard stat callbacks, `sparx5_update_stats()`, and delayed work `sparx5_check_stats_work()`.

## Control Flow
Stats initialization allocates `sparx5->stats`, configures policer and queue counters, creates a single-thread workqueue, and schedules periodic polling. The worker updates every live port. Counter readers choose DEV register blocks for Base-R modes and ASM registers otherwise, then combine normal and PMAC counters. EtHTool callbacks refresh relevant counters before filling standard structures or custom arrays. Link ksettings and pause parameters are delegated to phylink. Timestamp info reports hardware capabilities when a PHC is registered, with a Sparx5-specific fallback when PTP is disabled.

## State And Persistence
The driver keeps `sparx5->stats` as a flat `n_ports_all * num_stats` u64 array. `queue_stats_lock` serializes XQS statistic view selection. Delayed work and workqueue pointers live in `sparx5`. Hardware counters are read and extended but not persisted to disk.

## Dependencies And Integration Points
The file integrates with ethtool, rtnl link stats, phylink, PTP clock registration, Sparx5/ASM/DEV/XQS/ANA register blocks, port mode helpers, and netdev ops that call `sparx5_get_stats64()`.

## Risks And Edge Cases
`sparx5_update_counter()` assumes hardware counters are read often enough to detect one wrap between polls. `sparx5_get_stats64()` does not refresh counters itself, so it can lag the delayed worker. XQS statistic view is shared hardware state, hence the mutex. Stats deinit assumes init completed far enough to create the workqueue. Port mode changes must keep Base-R versus ASM counter selection correct.

## Test Signals
Run `ethtool -S`, standard ethtool stats, `ip -s link`, pause and link-setting operations, PTP timestamp capability queries, long traffic runs to test wrap extension, queue drops, policer drops, and unload while stats work is pending.
