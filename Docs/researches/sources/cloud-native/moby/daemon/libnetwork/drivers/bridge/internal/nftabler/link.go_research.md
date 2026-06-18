<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/link.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/link.go

## Purpose
Implements legacy container link firewall rules for the nftables backend.

## Important APIs, Types, And Functions
`AddLink` validates parent and child IP addresses, creates per-port rules with `updateLegacyLinkRules`, and applies them to the IPv4 table. `DelLink` deletes the same rules and logs apply failures.

## Control Flow
For each exposed port, two rules are generated in the network's filter-forward ingress chain: parent-to-child destination-port accept and child-to-parent source-port accept for unsolicited reverse traffic.

## State And Persistence
State is per-network nftables filter rules grouped under `fwdInLegacyLinksRuleGroup`. The code currently uses `table4`, reflecting legacy link behavior for IPv4 container addresses.

## Dependencies And Integration Points
Uses `nftables.Modifier`, `types.TransportPort`, `netip`, and logging. Called by bridge link programming and mirrored conceptually by iptabler link handling.

## Risks And Edge Cases
Delete is best-effort. The implementation does not combine rules into sets yet, so many linked ports produce many rules. IPv6 legacy link behavior is not represented here.

## Test Signals
Nftabler golden tests include legacy link rule groups as part of the backend lifecycle; bridge link tests validate driver behavior with the stub firewaller.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/link.go -->
