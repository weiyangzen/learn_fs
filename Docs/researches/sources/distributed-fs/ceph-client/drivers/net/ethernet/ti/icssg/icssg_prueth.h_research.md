<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.h

## Purpose

`icssg_prueth.h` is the central internal header for the ICSSG Ethernet driver. It defines port/MAC IDs, queue/channel state, TX software descriptor metadata, per-port EMAC state, top-level PRUETH device state, timestamp response layouts, constants for MTU, firmware commands, VLAN defaults, XDP results, coalescing, and prototypes shared across ICSSG source files.

## Important APIs, Types, and Functions

Core types are `struct prueth_tx_chn`, `struct prueth_rx_chn`, `struct prueth_swdata`, `struct prueth_emac`, `struct prueth_pdata`, `struct icssg_firmwares`, `struct prueth`, `struct emac_tx_ts_response`, and `struct emac_tx_ts_response_sr1`. Important helpers include `prueth_emac_slice()`, `icssg_read_time()`, prototypes for classifier/config/queue/FDB/stats/common RX/TX/timestamp/core-management helpers, and `prueth_xdp_is_enabled()`.

## Control Flow

The header has no executable lifecycle beyond inline helpers. `prueth_emac_slice()` maps MII0/MII1 port IDs to slice indexes and returns `-EINVAL` for invalid ports. `icssg_read_time()` performs a stable high/low 64-bit read by rechecking the high word.

## State and Persistence Behavior

`struct prueth` persists device-wide ownership of PRUSS cores, shared SRAM, SRAM pool, regmaps, IEPs, mode flags, firmware names, bridge/HSR state, VLAN table lock, and stats lock. `struct prueth_emac` persists per-netdev PHY/link state, DMA/NAPI/channel state, timestamp slots, command completion, RX mode work, stats arrays, VLAN multicast lists, XDP program and AF_XDP queue registration.

## Dependencies and Integration Points

The header includes Linux networking, PHY, remoteproc, PRUSS, PTP, DMA, page-pool, XDP, AF_XDP, `icssg_config.h`, `icss_iep.h`, and `icssg_switch_map.h`. It is included by nearly every ICSSG C file and forms the private cross-file ABI.

## Risks and Edge Cases

Many fields have implicit concurrency rules enforced outside the type definitions: `cmd_lock`, `stats_lock`, `vtbl_lock`, NAPI state, workqueue cancellation, and XDP pointer updates. `PRUETH_MAX_TX_QUEUES` is 4, while SR1 reserves a management channel and presents fewer queues to users. Packed TX timestamp response layouts differ between SR1 and SR2. Changes to `struct prueth_swdata` must remain within `PRUETH_NAV_SW_DATA_SIZE`, enforced by a build bug in the main driver.

## Test Signals

Compile all ICSSG objects together with SR1/SR2 platform variants, XDP sockets, HSR, PTP, and switchdev enabled. Runtime tests should stress concurrent link changes, open/close, timestamping, stats reads, XDP attach, AF_XDP pool changes, bridge and HSR mode transitions, and DMA teardown to validate the state model described by these structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.h -->
