# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth.c

## Purpose
This is the platform and net_device implementation for the TI PRUSS ICSSM Ethernet driver. It supports single/dual EMAC operation and runtime switch-mode offload when the two PRU Ethernet ports are enslaved to the same Linux bridge. It programs PRUSS DRAM/shared RAM/OCMC memory layouts, configures MII_RT, binds PHYs, boots PRU remoteproc firmware, handles NAPI RX, queues TX into firmware-owned rings, and registers netdevice and switchdev notifiers.

## Important APIs, types, and functions
- `icssm_prueth_probe()` discovers DT `ethernet-ports`, obtains PRU remoteprocs, PRUSS memory regions, shared SRAM/OCMC pool, MII_RT regmap, IEP, creates netdevices, registers them, and registers bridge/switchdev notifiers.
- `icssm_prueth_netdev_init()` allocates each `net_device`, initializes `struct prueth_emac`, maps port IDs to PRU/DRAM/TX/RX queues, obtains IRQ and PHY, installs `emac_netdev_ops`, NAPI, and a TX retry hrtimer.
- `icssm_emac_ndo_open()` and `icssm_emac_ndo_stop()` are the main lifecycle hooks. Open initializes shared memory on first port, configures EMAC or switch memory, initializes PTP/IEP once, boots firmware, requests IRQ, enables NAPI/PHY/port, and marks `emac_configured`. Stop clears the bit, disables port/PHY/NAPI/timer, shuts down firmware if no remaining port needs it, frees IRQ/FDB state, and exits IEP when the last port stops.
- `icssm_prueth_tx_enqueue()`, `icssm_emac_ndo_start_xmit()`, `icssm_emac_rx_packets()`, and `icssm_emac_rx_packet()` implement the shared-memory datapath.
- `icssm_prueth_change_mode()`, `icssm_prueth_ndev_port_link()`, `icssm_prueth_ndev_port_unlink()`, and `icssm_prueth_port_offload_fwd_mark_update()` handle bridge membership and firmware mode changes.
- `icssm_emac_ndo_set_rx_mode()` programs promiscuous and multicast filter state in firmware memory.

## Control flow
Probe is DT-driven: it validates at least one available port, gets PRU0/PRU1 if corresponding ports exist, configures PRUSS GPI/MII_RT/XFR, requests PRUSS DRAM/shared RAM regions, allocates OCMC SRAM, initializes netdevs, obtains IEP, registers netdevs, then registers notifiers. Each netdev open copies any user-changed MAC from `ndev->dev_addr`, initializes host memory only once, configures per-port memory, initializes FDB when in switch mode, starts IEP and firmware, requests RX IRQ, enables NAPI, starts the PHY, and sets the firmware port-control byte. RX IRQ only disables the IRQ and schedules NAPI. NAPI walks host queues, parses buffer descriptors from shared RAM, copies packet bytes out of OCMC, updates ring read pointers, and re-enables the IRQ when budget is not exhausted. TX maps VLAN PCP to one of four firmware queues, pads the skb, checks ring space, copies bytes into OCMC, writes a length descriptor, advances the write pointer, and frees or defers the skb based on queue availability.

Bridge events drive mode changes. When both PRU ports are members of the same bridge, `offload_fwd_mark` is enabled and the driver restarts active netdevs into `PRUSS_ETHTYPE_SWITCH`; when no bridge members remain, it restarts them into dual EMAC mode.

## State and persistence behavior
All persistent driver state is kernel runtime state: `struct prueth`, `struct prueth_emac`, PRUSS memories, OCMC buffers, PHY state, PRU remoteproc firmware state, notifier blocks, and NAPI/timer state. Firmware-visible state lives in PRUSS DRAM/shared RAM and OCMC, including queue descriptors, read/write pointers, port status/control bytes, MAC address, multicast table, PTP control block, and switch FDB when enabled. `emac_configured` coordinates shared initialization and firmware lifetime across two Linux netdevs. `br_members` and `hw_bridge_dev` track bridge offload eligibility.

## Dependencies and integration points
The file depends on Linux netdev, PHY, bridge, VLAN, multicast, notifier, NAPI, hrtimer, platform device, OF, PRUSS remoteproc, PRUSS memory, genalloc SRAM, syscon/regmap MII_RT, and ICSS IEP APIs. It shares constants and structures with `icssm_prueth.h`, `icssm_switch.h`, `icssm_prueth_switch.h`, `icssm_vlan_mcast_filter_mmap.h`, `icssg_mii_rt.h`, and `icss_iep.h`. External visible integration includes firmware files under `ti-pruss/*prueth-fw.elf` and `*prusw-fw.elf`, DT compatibles `ti,am57-prueth`, `ti,am4376-prueth`, and `ti,am3359-prueth`, and Linux bridge/switchdev offload.

## Risks and edge cases
- Hard-coded firmware memory offsets and queue sizes can corrupt queues if firmware ABI changes.
- TX/RX rings are manually managed by pointer arithmetic over 16-bit descriptor offsets; wrap handling is critical.
- Mode changes stop and reopen running netdevs; partial restart failure can leave ports in mixed state.
- Switch mode assumes both PRUs and both physical ports are available, while probe permits single-port operation.
- RX packet length validation avoids lockup by advancing to the firmware write pointer, losing queued packets in that queue.
- Multicast hash is a simple XOR masked by six bytes, so collisions can over-permit traffic.

## Test signals
Useful tests include DT probe success/failure for one-port and two-port nodes, `ip link set up/down` in EMAC and switch modes, bridge enslave/unenslave mode transitions, RX/TX traffic with VLAN PCP classes, queue-full TX retry behavior, multicast/promiscuous/allmulti changes, invalid or oversized RX descriptors from firmware, suspend/resume with running interfaces, firmware missing or boot failure, and resource unwind paths from probe failures.
