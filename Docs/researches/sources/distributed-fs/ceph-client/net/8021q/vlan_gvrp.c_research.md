<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_gvrp.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_gvrp.c

This file adapts generic GARP to VLAN GVRP. It defines a single `garp_application` for VLAN ID attributes sent to multicast address `01:80:c2:00:00:21`.

`vlan_gvrp_request_join()` and `vlan_gvrp_request_leave()` extract the VLAN id from the VLAN device, encode it big-endian, and call `garp_request_join()` or `garp_request_leave()` on the real device for `GVRP_ATTR_VID`. They are no-ops for non-802.1Q VLAN protocols. Applicant lifecycle is delegated to `garp_init_applicant()`/`garp_uninit_applicant()`, and module lifecycle registers/unregisters the GARP application.

State is the static application descriptor plus per-real-device applicant state managed by `garp.c`. Dependencies are VLAN device private data, GARP APIs, and 802.1Q ethertype filtering.

Risks include advertising S-tag/802.1ad VLANs by mistake, byte-order errors in VID attributes, and missing applicant initialization before request calls. Tests should enable the VLAN GVRP flag on 802.1Q and 802.1ad devices, verify only 802.1Q emits requests, and validate applicant init/uninit around first/last VLAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_gvrp.c -->
