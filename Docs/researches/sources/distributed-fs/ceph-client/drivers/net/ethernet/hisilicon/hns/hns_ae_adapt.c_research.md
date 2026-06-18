# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ae_adapt.c

## Purpose
`hns_ae_adapt.c` adapts the DSAF hardware implementation to the generic HNAE framework. It allocates HNAE handles from DSAF RCB ring-pair resources, translates AE operations into MAC/PPE/RCB/DSAF calls, composes stats and register dumps, and registers the DSAF AE device.

## Important APIs and Functions
`hns_dsaf_ae_init` and `hns_dsaf_ae_uninit` register/unregister the AE. The `hns_dsaf_ops` table implements HNAE callbacks: handle allocation, queue init/fini, start/stop/reset, ring IRQ toggles, link state and adjustment, MAC address management, multicast/unicast operations, MTU, TSO, pause, coalescing, promisc, stats, strings, LEDs, register dumps, and RSS. `hns_ae_get_handle` allocates `struct hnae_vf_cb`, chooses unused ring-pair blocks, and populates `struct hnae_handle` metadata from the selected MAC control block.

## Control Flow
Handle creation calculates queue and VF counts from `rcb_common[0]`, scans ring pairs for an unused VF slot, marks each ring pair used, then binds handle queues to those RCB queue objects. Start enables broadcast reception, clears TX/RX interrupts, enables all rings, waits, then starts the MAC. Stop drains TX, stops the MAC, disables rings, drains RX, and disables broadcast. Link adjustment on v2 disables MAC RX, waits for RCB/PPE/DSAF/MAC flow-down, changes link settings, then re-enables RX.

## State and Persistence
State is in the DSAF device and handle structures: ring-pair `used_by_vf` flags, VF identifiers, MAC metadata, shadow RSS key/indirection table in PPE, coalescing parameters, and accumulated hardware stats in RCB/PPE/MAC/DSAF structures. No persistent storage is used.

## Dependencies and Integration Points
This file sits between HNAE and `hns_dsaf_mac.c`, `hns_dsaf_main.c`, `hns_dsaf_ppe.*`, and `hns_dsaf_rcb.*`. It is the main integration point consumed by the upper Ethernet driver through `hnae_ae_ops`. It also adapts version-specific IRQ programming by selecting `hns_ae_toggle_ring_irq` for AE v1 and `hns_aev2_toggle_ring_irq` for AE v2.

## Risks
`hns_dsaf_ops` is a static mutable global, and `hns_dsaf_ae_init` changes its `toggle_ring_irq` pointer based on the registering device version. Mixed v1/v2 devices in one kernel could race or receive the wrong callback. `hns_ae_get_handle` only uses `rcb_common[0]`, so multi-common-device assumptions are narrow. Start/stop sequencing relies on fixed sleeps and polling. Multicast setup adds both MAC and VF inner ports, making TCAM cleanup correctness important.

## Test Signals
Probe tests should verify AE registration for v1 and v2, handle allocation exhaustion, ring-pair `used_by_vf` cleanup, start/stop under traffic, v2 link adjustment while packets are draining, RSS get/set consistency, ethtool stats/string counts, and interrupt mask behavior for both RCB versions.
