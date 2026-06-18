# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_util.h

Purpose: shared utility helpers for usNIC addressing.

Important APIs: `usnic_mac_ip_to_gid()` builds a link-local style raw GID using `fe80`, the IPv4 address in bytes 4..7, and an EUI-48-derived interface identifier from the MAC address.

Control flow: device add/query paths call this helper to populate node GUID, sys image GUID, and query-GID responses based on the current PF MAC/IP state.

State and persistence: no state; output depends on caller-provided MAC and IPv4 address.

Dependencies and integration: depends on `addrconf_addr_eui48()` from IPv6 addrconf and is used by `usnic_ib_main.c` and `usnic_ib_verbs.c`.

Risks: GID identity changes when MAC/IP changes; notifier code must dispatch GID change events and move active QP groups to error. If no IP exists, the generated GID contains a zero IPv4 field.

Test signals: query-GID output before/after IPv4 address changes, node GUID generation during probe, and GID change event delivery.
