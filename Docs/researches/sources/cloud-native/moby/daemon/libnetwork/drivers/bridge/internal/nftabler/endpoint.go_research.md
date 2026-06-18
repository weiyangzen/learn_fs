<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/endpoint.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/endpoint.go

## Purpose
Programs per-endpoint direct-access filtering for the nftables backend.

## Important APIs, Types, And Functions
`AddEndpoint` optionally invokes the stored cleaner, then calls `modEndpoint`. `DelEndpoint` removes rules. `filterDirectAccess` builds raw prerouting drop rules using family-specific `daddr`, the bridge interface, and trusted host interfaces.

## Control Flow
For each enabled family and valid endpoint address, create/delete a modifier against the family table. Filtering is skipped for internal, unprotected, routed, or daemon-wide direct-routing configurations. Otherwise packets addressed to the container from interfaces outside the bridge/trusted set are dropped.

## State And Persistence
State is nftables raw-prerouting rules in the backend-owned table. Cleaner calls remove old backend rules during live-restore before nftables rules are added.

## Dependencies And Integration Points
Uses internal `nftables`, `firewaller.NetworkConfigFam`, `netip`, and string formatting for interface sets. Called by bridge endpoint creation/removal and store restore.

## Risks And Edge Cases
Trusted interface formatting can produce an empty set element if no trusted interfaces exist, so rule generation depends on nftables helper behavior. Direct-routing flags are security-sensitive. Unlike iptabler, there is no raw-rule environment opt-out in this backend.

## Test Signals
Nftabler golden tests cover endpoint rule output across routed, unprotected, internal, direct filtering, and WSL2-related combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/endpoint.go -->
