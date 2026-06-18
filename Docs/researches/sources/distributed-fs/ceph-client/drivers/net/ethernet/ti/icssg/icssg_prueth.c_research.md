<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.c

## Purpose

`icssg_prueth.c` is the main SR2/non-SR1 platform driver for TI PRUSS ICSSG Ethernet. It owns probe/remove, netdev creation, PHY connection, PRU/RTU/TX_PRU firmware boot, common start/stop, link adjustment, PTP clock integration, TX timestamp handling, DMA queue bring-up/teardown, multicast/VLAN/FDB synchronization, bridge switchdev mode transitions, HSR/PRP offload mode transitions, XDP/AF_XDP hooks, and netdevice/switchdev notifier registration.

## Important APIs, Types, and Functions

The file defines `emac_netdev_ops`, platform `prueth_driver`, platform data for AM654 and AM64x, `prueth_iep_clockops`, `prueth_dev_check()`, and `prueth_xsk_wakeup()`. Important internal routines include `prueth_emac_common_start/stop()`, `prueth_emac_start/stop()`, `emac_adjust_link()`, `emac_ndo_open/stop()`, multicast and HSR FDB helpers, VLAN add/delete, `emac_ndo_bpf()`, `emac_xdp_xmit()`, `prueth_netdev_init()`, bridge/HSR link/unlink handlers, notifier callbacks, firmware-name generation, `prueth_probe()`, and `prueth_remove()`.

## Control Flow

Probe parses `ethernet-ports`, gets regmaps, PRUSS cores, shared RAM, SRAM pool, IEPs, firmware names, and creates/registers netdevs. `ndo_open` initializes TX/RX DMA channels and NAPI, requests RX and TX timestamp IRQs, starts common firmware on the first active port, writes RX flow IDs, enables queues, starts PHY, and starts stats work. Common start clears SRAM/SHRAM, configures classifier defaults and HSR filtering, initializes EMAC or offload mode, configures each slice, boots firmwares, and initializes IEP. Link changes update duplex/speed, IPG, RGMII config, firmware speed byte, and port state. Bridge or HSR upper-device events restart firmware into switch/HSR/PRP firmware mode once both physical ports participate.

## State and Persistence Behavior

Persistent runtime state spans `struct prueth` mode flags (`is_switch_mode`, `is_hsr_offload_mode`), bridge/HSR membership bitmaps, `default_vlan`, firmware name arrays, registered netdevs, PRUSS memory regions, IEP handles, `emacs_initialized`, multicast shadow lists, XDP/XSK pointers, DMA channels, NAPI, TX timestamp skb slots, coalescing timers, VLAN/PVID/FDB firmware state, and shared-memory time sync descriptors. Mode changes persist until bridge/HSR unlink or device removal.

## Dependencies and Integration Points

The file integrates with remoteproc/pruss APIs, syscon regmaps, genalloc SRAM, K3 UDMA glue, CPPI descriptor pools, PHY/MDIO, netdevice ops, switchdev, bridge, HSR/PRP helpers, XDP/AF_XDP, page-pool, PTP/IEP, classifier helpers, common TX/RX helpers from `icssg_common.c`, config helpers, stats work, and firmware files named from DT.

## Risks and Edge Cases

Mode changes restart both ports and require both netdevs to exist; failures can leave devices detached or firmware stopped until recovery. HSR multicast membership has complex refcount/synced handling and must avoid sleeping under address locks. XSK enable/disable tears RX down while running and must restore port state on every failure path. TX timestamp cookies are bounded by `PRUETH_MAX_TX_TS_REQUESTS`; invalid firmware cookies produce errors and may leak pending state. Firmware-name replacement silently falls back to the original string if replacement/allocation fails. Probe error unwind spans many resources and needs platform-specific coverage.

## Test Signals

Use dual-port and single-port probe/remove, repeated `ip link set up/down`, PHY speed changes, PTP get/set/perout and TX/RX timestamp tests, bridge enslave/leave with VLAN/MDB/FDB operations, HSR and PRP offload attach/detach, multicast sync on physical/VLAN/HSR devices, XDP attach/detach, AF_XDP bind/unbind and wakeup, fault injection in DMA/channel/IRQ/firmware boot paths, and traffic under mode restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth.c -->
