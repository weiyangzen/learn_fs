<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.c

## Purpose

`icssg_stats.c` accumulates ICSSG hardware counters into per-port software counters and provides periodic refresh and name-based lookup for ethtool/RMON/stat64 consumers.

## Important APIs, Types, and Functions

Exported functions are `emac_update_hardware_stats()`, `icssg_stats_work_handler()`, and `emac_get_stat_by_name()`. It uses `stats_base[]` for per-slice MIIG counter base offsets and stat metadata from `icssg_stats.h`.

## Control Flow

`emac_update_hardware_stats()` locks `prueth->stats_lock`, walks MIIG stats, reads each hardware counter, writes the same value back to clear it, accumulates into `emac->stats`, adjusts TX byte count by subtracting 8 bytes per packet, then optionally reads PA stats into `emac->pa_stats`. `icssg_stats_work_handler()` refreshes and reschedules itself based on link speed. `emac_get_stat_by_name()` linearly searches MIIG then PA stat tables.

## State and Persistence Behavior

The file persists cumulative counters in `emac->stats[]` and `emac->pa_stats[]`. It clears MIIG hardware counters on each read-by-writeback. PA stat reads are accumulated without an explicit clear in this file. Periodic work persists while the netdev is open and is canceled on stop.

## Dependencies and Integration Points

It depends on `icssg_prueth.h`, `icssg_stats.h`, `regmap`, and spinlocks. Ettool stats, RMON stats, and netdev stats paths consume the accumulated arrays.

## Risks and Edge Cases

In MII mode, TX counters are read from the opposite slice, but `base` is not reset inside each loop iteration after being changed; subsequent non-TX counters could read the swapped base depending on ordering. `emac_get_stat_by_name()` returns `int` from `u64` counters, risking truncation. The work reschedule divides by `emac->speed`, so speed must be a valid nonzero link speed before work runs.

## Test Signals

Generate RX/TX traffic in MII and RGMII modes, compare ethtool stats with packet counters, validate TX byte adjustment, run with and without PA stats regmap, stress periodic stats at 10/100/1000 speeds, and use RMON stat lookup after high-volume traffic to catch truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.c -->
