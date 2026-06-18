# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/peerdb_windows.go

Purpose: wires Windows overlay peer discovery events into HNS remote endpoint records. Important functions are `peerAdd` and `peerDelete`; they are invoked by overlay/networkdb peer synchronization paths to add or remove remote container attachment information.

Control flow: both functions validate network and endpoint IDs, look up the overlay network in the driver's table, and no-op if the network is absent. `peerAdd` creates an `hcsshim.HNSEndpoint` marked `IsRemoteEndpoint`, attaches a PA policy carrying the VTEP/provider address, converts the peer IP to `/32`, removes any stale endpoint with that address, posts the HNS endpoint, then stores an overlay `endpoint` with `remote: true` and the returned HNS profile ID. `peerDelete` finds the endpoint, calls HNS delete by `profileID`, and removes it from the network table.

State and dependencies: state is split between HNS remote endpoints and the overlay network's endpoint table. Dependencies are `hcsshim`, JSON policy encoding, `types.ParseCIDR`, and package-local `validateID`/network lookup. Risks include errors when deleting unknown peers, reliance on HNS-generated IDs, and lack of IPv6 remote peer handling. Test coverage is not local in this file.
