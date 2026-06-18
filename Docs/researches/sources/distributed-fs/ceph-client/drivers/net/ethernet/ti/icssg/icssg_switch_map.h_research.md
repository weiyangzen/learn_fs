<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switch_map.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switch_map.h

## Purpose

`icssg_switch_map.h` is the firmware shared-memory map for ICSSG switch/EMAC features. It names offsets for FDB/VLAN configuration, packet descriptor memory, time sync descriptors, TAS/preemption controls, flow IDs, queue mappings, link speed, buffer pools, R30 commands, host RX queue contexts, FDB command buffer, half-duplex seed, and PA statistics.

## Important APIs, Types, and Functions

The file defines constants only. Major groups are FDB sizing and firmware speed codes, default VLAN offsets for host/P1/P2, VLAN table offset, descriptor-memory offsets, time sync offsets, TAS offsets, queue and priority mapping offsets, preemption offsets, `MGR_R30_CMD_OFFSET`, `BUFFER_POOL_0_ADDR_OFFSET`, host RX queue context offsets, `FDB_CMD_BUFFER`, `HD_RAND_SEED_OFFSET`, and `FW_*` PA stat offsets.

## Control Flow

There is no control flow. These offsets are used by config, main driver, stats, timestamp, PVID, FDB, and link-adjustment code when reading or writing shared RAM and PA stat regmaps.

## State and Persistence Behavior

The constants describe persistent firmware-visible memory layout. Writes to these offsets configure firmware behavior and remain active until the shared memory is cleared, firmware restarts, or the device resets.

## Dependencies and Integration Points

Included by `icssg_prueth.h` and `icssg_config.c`, this header is a shared ABI between Linux driver and ICSSG firmware. `icssg_stats.h` uses PA stat offsets from this map, and PTP/IEP code uses the time sync offsets.

## Risks and Edge Cases

Any offset drift from firmware breaks behavior without type checking. FDB bucket size comments explicitly tie constants to ageing calculation. Several features such as TAS and preemption have offsets even if not fully managed by this subset, so future feature work must preserve existing layout.

## Test Signals

Regression tests should validate PVID/VLAN table writes, FDB command buffer lookups, firmware speed updates, PTP settime/perout, PA stat reads, R30 port-state commands, and buffer-pool initialization after firmware updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switch_map.h -->
