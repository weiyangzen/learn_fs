<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/link.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/link.go

## Purpose
Implements legacy container link firewall rules for the iptables backend.

## Important APIs, Types, And Functions
`AddLink` validates parent/child IP addresses and appends rules through `iptables.ChainInfo.Link`. `DelLink` deletes matching rules and logs failures.

## Control Flow
For each exposed transport port, add or delete a rule in the `DOCKER` chain allowing traffic between a parent container IP and child container IP on the bridge interface.

## State And Persistence
State is per-link iptables filter state in the `DOCKER` chain. The bridge driver tracks which links exist and calls deletion on disconnect; this file does not store refcounts.

## Dependencies And Integration Points
Uses `iptables.ChainInfo`, `types.TransportPort`, `netip`, and containerd logging. Called by bridge external-connectivity/link logic and covered indirectly by link tests.

## Risks And Edge Cases
Invalid or unspecified IPs are rejected on add. Delete is best-effort and only logs failures, so stale link rules could remain after partial cleanup. It is IPv4-oriented through legacy `ChainInfo.Link` behavior.

## Test Signals
`TestLinkContainers` with the stub firewaller validates the driver-level link lifecycle; iptabler golden tests include link rule groups through backend operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/link.go -->
