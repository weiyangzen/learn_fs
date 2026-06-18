# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.c

## Purpose
`enic_res.c` is the Cisco ENIC resource orchestration layer. It reads firmware-provided vNIC configuration, issues ENIC-specific device commands for VLAN/RSS/NIC settings, counts and allocates hardware resources, initializes WQ/RQ/CQ/interrupt MMIO blocks, and negotiates extended receive completion queue entry size.

## Important APIs, types, and functions
- `enic_get_vnic_config()` fetches MAC address and selected `struct vnic_enet_config` fields with `vnic_dev_get_mac_addr()` and `vnic_dev_spec()`, clamps queue lengths/MTU/coalescing values, aligns WQ/RQ descriptors to 32-entry groups, and logs the effective feature set.
- `enic_add_vlan()` / `enic_del_vlan()` wrap `CMD_VLAN_ADD` and `CMD_VLAN_DEL`.
- `enic_set_nic_cfg()` builds the NIC config word via `vnic_set_nic_cfg()` and uses `CMD_NIC_CFG_CHK` when UDP RSS hash bits are requested.
- `enic_set_rss_key()` and `enic_set_rss_cpu()` pass DMA buffers to `CMD_RSS_KEY` and `CMD_RSS_CPU`.
- `enic_get_res_counts()` reads firmware BAR resource counts and detects an admin channel by checking admin WQ/RQ/CQ plus SR-IOV interrupt availability.
- `enic_alloc_vnic_resources()` allocates ENIC WQs, RQs, CQs, interrupt controls, and legacy PBA resources.
- `enic_init_vnic_resources()` programs queues and CQs with CQ and interrupt indices based on interrupt mode.
- `enic_ext_cq()` uses `CMD_CAPABILITY` and `CMD_CQ_ENTRY_SIZE_SET` under `devcmd_lock` to select 16/32/64 byte RQ CQ entries.

## Control flow and state
Configuration flow is firmware-first: the driver asks the vNIC firmware for MAC/config fields, applies kernel-side defaults and bounds, then later uses those values to size descriptor rings. Allocation flow is WQ, RQ, CQ, interrupt, then optional legacy PBA. Any allocation error jumps to cleanup through `enic_free_vnic_resources()`. Initialization flow maps RQs to early CQs and WQs to later CQs, then maps CQs to interrupt vector 0 for INTx/MSI or per-CQ MSI-X vectors. Error interrupt wiring is enabled for INTx and MSI-X but not MSI.

State is mostly in `struct enic`: effective config, resource counts, `ext_cq`, ring objects, interrupt objects, `legacy_pba`, and admin-channel availability. Persistent hardware state is written through vNIC MMIO registers by the lower-level `vnic_*_init()` helpers and firmware devcmds.

## Dependencies and integration points
This file depends on the ENIC top-level `struct enic` and on descriptor, vNIC resource, device-command, queue, CQ, interrupt, RSS, NIC config, and stats headers. It is used during probe/open/reset paths to establish the ENIC hardware datapath before TX/RX NAPI begins. Firmware capability behavior in `vnic_dev.c` determines whether newer features such as extended CQ entries are available.

## Risks and test signals
Key risks are resource-count mismatches, invalid `ext_cq` selection, incorrect CQ-to-queue mapping, unsupported firmware commands, and missing legacy PBA in INTx mode. Useful test signals include probe logs for effective WQ/RQ/CQ/intr counts, VLAN add/delete errors, RSS programming success, interrupt-mode-specific packet I/O, and fallback logging when `CMD_CQ_ENTRY_SIZE_SET` is unavailable or fails.
