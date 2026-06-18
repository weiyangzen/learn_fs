# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_utils.go

Purpose: Provides Linux overlay utility helpers for id validation, veth creation, VXLAN creation/deletion, and VNI-based VXLAN cleanup.

Important APIs and functions: `validateID` checks network and endpoint ids. `createVethPair` generates two veth names and creates a `netlink.Veth`. `createVxlan` creates a VXLAN link with learning/proxy/L2miss/L3miss enabled and configurable UDP port; it sets IPv6 unspecified group when VTEP addresses are IPv6. `deleteInterface` deletes a named link. `deleteVxlanByVNI` can operate in a specified network namespace and delete the first matching VXLAN by VNI or any VXLAN when VNI is zero.

Control flow: namespace-specific VXLAN deletion opens a netns handle and netlink handle with socket timeout, lists links, and deletes matching VXLAN.

State and persistence: mutates Linux link state; no datastore.

Dependencies and integration points: used by overlay join/network cleanup. Depends on `netutils`, `netlink`, `netns`, `nlwrap`, and `overlayutils.VXLANUDPPort`.

Risks: `deleteVxlanByVNI` deletes only the first matching VXLAN. Link generation and creation can race with other processes. VXLAN VTEP family must match peer family.

Test signals: no direct tests in this subset.
