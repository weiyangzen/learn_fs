<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.h

Purpose: declares the shared NIC object model and public NIC control API used by PCI, netdev, vector, ring, PTP, filter, ethtool, and hardware layers.

Important APIs/types: defines `enum aq_fc_mode`, `struct aq_fc_info`, `struct aq_nic_cfg_s`, filter bookkeeping structs, and `struct aq_nic_s`. It declares lifecycle functions (`aq_nic_init`, `aq_nic_start`, `aq_nic_stop`, `aq_nic_deinit`, `aq_nic_shutdown`), TX functions, stats/register accessors, link settings, filter reservation, and TC configuration helpers. Macros map traffic class/vector IDs to hardware ring indices.

Control flow: consumers fill `aq_nic_cfg_s` from hardware capabilities, then drive the declared lifecycle in probe/open/close/remove/PM paths. Rings and vectors call back into `aq_nic_get_ndev`, `aq_nic_get_cfg`, and ring mapping macros to coordinate queue numbering.

State and persistence: `aq_nic_s` centralizes atomic flags, `aq_hw_s`, ops tables, netdev, PCI device, vector/ring arrays, timers, link state, multicast/VLAN state, firmware request mutex, optional MACsec, optional PTP, and RX filter reservations. This is runtime kernel state only.

Dependencies and integration: includes ethtool, XDP/BPF, `aq_common`, `aq_rss`, and `aq_hw`. It is included broadly by the Atlantic driver and forms the common ABI between generic and hardware-specific files.

Risks: macro ring mapping must stay synchronized with TC mode and vector count; flags are bit constants shared across asynchronous paths; optional fields under Kconfig require callers to tolerate absent MACsec/PTP support. Test signals are compile coverage for all include users, queue mapping tests through multiqueue TX/RX, and runtime transitions that mutate `aq_nic_cfg_s`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.h -->
