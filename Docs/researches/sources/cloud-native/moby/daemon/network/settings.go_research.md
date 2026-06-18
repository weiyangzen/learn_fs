# sources/cloud-native/moby/daemon/network/settings.go

## Purpose
This file defines daemon-persisted network settings for containers and an attachment store for swarm load-balancer IPs.

## Important APIs, Types, And Functions
`Settings` stores sandbox IDs/keys, endpoint settings, service config, ports, and swarm endpoint state. `EndpointSettings` wraps API endpoint settings with internal fields `IPAMOperational` and `DesiredMacAddress`. `AttachmentStore` maps network IDs to LB IPs with methods `ResetAttachments`, `ClearAttachments`, `clearAttachments`, and `GetIPForNetwork`.

## Control Flow
`ResetAttachments` locks the store, clears existing state, parses each CIDR string, stores parsed IPs by network ID, and resets to an empty map on parse failure. `ClearAttachments` and `GetIPForNetwork` are mutex-protected. `clearAttachments` initializes the map.

## State, Persistence, And Dependencies
`Settings` is persisted as part of container network state; `AttachmentStore` is in-memory daemon/cluster state. Dependencies include API network types, cluster service config, `net`, `sync`, and errors wrapping.

## Integration Points
`network.go` uses `AttachmentStore.GetIPForNetwork` when creating agent overlay networks with load-balancer endpoints. Container networking code uses `Settings.Networks` to build endpoint options and persist endpoint info.

## Risks And Edge Cases
On any CIDR parse error, `ResetAttachments` discards all attachment mappings. `GetIPForNetwork` returns the stored `net.IP` slice directly, so callers should not mutate it. The comment notes Windows-specific factoring is incomplete.

## Test Signals
No direct tests in this item; behavior is covered indirectly by swarm networking paths.
