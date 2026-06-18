## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.c

Purpose: implements RX classification filters for ethtool NFC and VLAN offload on Atlantic hardware.

Important APIs/types: uses `struct aq_rx_filter` hlist nodes from `aq_filters.h` and hardware filter tables in `aq_hw_rx_fltrs_s`. Public functions include count/get/add/delete/list/clear/reapply NFC rules, VLAN deletion by VID, VLAN filter update, and VLAN offload disable.

Control flow: add validates flow type, location, masks, queue action, duplicate matching, and feature enablement. Rules are classified as ethertype/L2, VLAN, or L3/L4. L2 rules program `hw_filter_l2_set/clear`; VLAN rules update the shared VLAN filter array and call `aq_filters_vlans_update()`; L3/L4 rules populate protocol/address/port commands and call hardware L3/L4 programming. The software hlist is kept ordered by location. Open and feature transitions reapply or clear rules. VLAN update rebuilds limited hardware slots so queue-assigned VLAN rules take precedence over plain active VLANs, toggles hardware VLAN filtering, and falls back to forced promiscuous behavior when active VLAN count exceeds hardware slots.

State and persistence: rules persist in memory across device stop/start via `aq_nic->aq_hw_rx_fltrs.filter_list` and are reapplied on open. Active VLAN bitmap is in `aq_nic->active_vlans`. No disk persistence.

Dependencies/integration: called by `aq_main.c` open, VLAN ndo operations, feature changes, and `aq_ethtool.c` RX NFC callbacks. Requires `aq_hw_ops` filter callbacks and queue/TC config from `aq_nic_cfg_s`.

Risks: L3/L4 hardware cannot mix IPv4 and IPv6 filters, and IPv6 locations are restricted to paired slots. VLAN table has only 16 entries and can enter forced-promiscuous mode. Rule insertion updates software before hardware programming and rolls back on hardware errors, so rollback correctness matters. Duplicate detection compares full specs except location.

Test signals: `ethtool -K ntuple on/off`, add/delete/list rules for ETHER/TCP/UDP/SCTP/IPv4/IPv6, duplicate and invalid-location rejection, VLAN add/kill under hardware slot pressure, interface reopen with rules, and hardware callback failure injection.
