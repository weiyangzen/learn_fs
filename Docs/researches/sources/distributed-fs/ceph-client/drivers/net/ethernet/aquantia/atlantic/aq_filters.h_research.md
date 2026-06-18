## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.h

Purpose: public RX filter interface for Atlantic.

Important APIs/types: defines `enum aq_rx_filter_type` for ethertype, VLAN, and L3/L4 filters; defines `struct aq_rx_filter` with hlist node, type, and saved `ethtool_rx_flow_spec`; declares all RX NFC and VLAN filter management functions.

Control flow: none in header.

State and persistence: `struct aq_rx_filter` is the in-memory persistence unit for ethtool rules across hardware resets/reopens.

Dependencies/integration: includes `aq_nic.h` for NIC structures; used by `aq_main.c` and `aq_ethtool.c`.

Risks: structure layout is internal but shared across filter implementation. API callers rely on add/delete/reapply functions to keep software and hardware state synchronized.

Test signals: compile and all ethtool NFC/VLAN paths.
