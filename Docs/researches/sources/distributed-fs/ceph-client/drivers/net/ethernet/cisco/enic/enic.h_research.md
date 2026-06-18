<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic.h

## Purpose

`enic.h` is the central private header for the Cisco VIC Ethernet driver. It defines supported PCI subsystem IDs, queue limits, interrupt layout, ENIC-private state structures, statistics, RFS flow tables, port-profile data, VXLAN state, helpers, logging wrappers, and internal prototypes shared by ENIC source files.

## Important APIs, Types, and Definitions

`struct enic` is the device-wide state: netdev, PCI device, vNIC config, BAR mappings, `vnic_dev`, timers/work items, MSI-X metadata, devcmd/API locks, MAC/filter counts, coalescing settings, SR-IOV and VF type state, port profiles, WQ/RQ/CQ/intr arrays, NAPI array, RSS key, generic stats, extended CQ selection, VXLAN state, and optional admin-channel resources.

Queue structures `struct enic_wq` and `struct enic_rq` wrap `vnic_wq`/`vnic_rq` with spinlocks/stats and page-pool state. `struct enic_rfs_fltr_node` and `struct enic_rfs_flw_tbl` store accelerated RFS IPv4 5-tuple filters. `struct enic_port_profile` stores port-profile requests, names, UUIDs, VF MACs, and MAC addresses. Interrupt helpers map RQ/WQ queues to CQ and MSI-X interrupt indices; `enic_dma_map_check` centralizes DMA mapping error accounting.

## Control Flow

The header itself has no top-level execution. Its inline helpers guide runtime mapping of queues, CQs, and interrupts in `enic_main.c`, while structures provide the state contract for ethtool, classifier, device-command, port-profile, RX, and TX helper modules.

## State and Persistence Behavior

All structures describe in-memory driver state. Some state mirrors firmware configuration, such as vNIC config, MAC address, port MTU, RSS key, coalescing timers, VXLAN UDP port, and port profiles. None is disk-persistent; it is rebuilt at PCI probe, device init, open, reset, or provisioning events.

## Dependencies and Integration Points

The header depends on ENIC vNIC helper headers, page-pool helpers, IRQ APIs, and netdev types. It is included across ENIC implementation files and exposes prototypes for `enic_reset_addr_lists`, SR-IOV checks, ethtool setup, RSS key programming, and extended CQ configuration.

## Risks and Edge Cases

Queue/CQ/interrupt mapping helpers are foundational; off-by-one errors would route completions to the wrong NAPI or interrupt. `ENIC_DESC_MAX_SPLITS` derives from TSO and descriptor length limits and affects TX ring fullness checks. RFS hash table sizing and bitfields constrain cleanup iteration. The API busy flag coordinates with exported ENIC API calls and reset paths, so lock ordering matters.

## Test Signals

Compile coverage across all ENIC objects, probe with different interrupt modes, RSS/RFS enabled builds, SR-IOV-enabled PFs and VFs, VXLAN feature negotiation, DMA mapping error injection, queue statistics, and reset paths validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic.h -->
