<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_mvrp.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_mvrp.c

This file adapts generic MRP to VLAN MVRP. It defines `vlan_mrp_app`, an MRP application for VLAN ID attributes using packet type `ETH_P_MVRP`, group address `01:80:c2:00:00:21`, and version 0.

Join and leave helpers encode the VLAN id as big-endian and call `mrp_request_join()` or `mrp_request_leave()` on the real device for `MVRP_ATTR_VID`. Like GVRP, requests are ignored for non-802.1Q VLAN protocols. Applicant lifecycle and application registration are delegated to the generic MRP layer.

State is a static descriptor plus per-device MRP applicants managed by `mrp.c`. Dependencies are VLAN private data, MRP APIs, packet type registration, and 802.1Q ethertype filtering.

Risks include incorrect VID byte order, unintended operation on 802.1ad VLANs, and mismatched MRP version/type. Tests should cover MVRP flag toggling, applicant startup/shutdown when VLANs appear/disappear, no-op behavior for non-802.1Q VLANs, and emitted MRP VLAN attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_mvrp.c -->
