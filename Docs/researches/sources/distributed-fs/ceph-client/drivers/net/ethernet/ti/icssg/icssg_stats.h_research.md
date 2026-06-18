<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.h

## Purpose

`icssg_stats.h` defines the ICSSG MIIG and PA statistic register layouts and metadata tables used by stats refresh and ethtool export.

## Important APIs, Types, and Functions

Important definitions are `STATS_TIME_LIMIT_1G_MS`, `struct miig_stats_regs`, `struct icssg_miig_stats`, `icssg_all_miig_stats[]`, `struct icssg_pa_stats`, and `icssg_all_pa_stats[]`. Macros `ICSSG_MIIG_STATS()` and `ICSSG_PA_STATS()` build metadata entries with names, offsets, and standard-stat flags.

## Control Flow

There is no executable flow. The ordered arrays drive loops in `icssg_stats.c` and ethtool string/count/data callbacks in `icssg_ethtool.c`.

## State and Persistence Behavior

The header describes hardware counter offsets and which counters are considered standard versus ethtool-private. The arrays are static const metadata and do not hold runtime state.

## Dependencies and Integration Points

It includes `icssg_prueth.h`, which supplies Ethernet string lengths, stat count constants, and PA stat offsets through `icssg_switch_map.h`. It is consumed by `icssg_stats.c` and `icssg_ethtool.c`.

## Risks and Edge Cases

Array sizes must remain consistent with `ICSSG_NUM_MIIG_STATS`, `ICSSG_NUM_PA_STATS`, `ICSSG_NUM_STANDARD_STATS`, and `ICSSG_NUM_ETHTOOL_STATS` from `icssg_prueth.h`. Offsets are derived with `offsetof(struct miig_stats_regs, field)`, so changing struct order changes the hardware ABI assumptions.

## Test Signals

Compile-time checks should compare array lengths against constants if added. Runtime validation should compare ethtool string count with returned data count, check all named RMON stats exist, and verify optional PA stats alter ethtool stat count as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_stats.h -->
