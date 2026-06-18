# sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager.go

## Purpose
Coordinates hostport management across IPv4/IPv6 and iptables/nftables backends. It prefers nftables for new rules, falls back to iptables, cleans both on removal for migration safety, filters mappings by IP family, and clears UDP conntrack entries after Add.

## Important APIs, Types, And Functions
- `metaHostportManager` maps `utilnet.IPFamily` to `hostportManagers`.
- `hostportManagers` holds optional iptables and nftables managers.
- `NewMetaHostportManager`, `newMetaHostportManagerInternal`, `Add`, `Remove`, and `filterHostportMappings` implement orchestration.
- `netlinkFamily` maps Kubernetes IP families to netlink families.

## Control Flow
Construction tries IPv4 iptables and nftables and fails only if both are unavailable. IPv6 backends are attempted but may be absent, with informational logging. `Add` determines pod IP family, filters invalid or mismatched mappings, errors if no manager exists for the family, selects nftables if present otherwise iptables, and then best-effort deletes UDP conntrack entries for host ports. `Remove` does not know pod IP, so it iterates all configured families, filters mappings by HostIP family, removes nftables entries when available, removes iptables entries too, and ignores iptables errors when nftables is primary.

## State And Persistence
Persists no state directly; delegates to backend kernel state. UDP conntrack deletion mutates kernel conntrack state. Manager availability is kept in memory.

## Dependencies And Integration Points
Integrates CRI-O iptables wrapper, knftables, Kubernetes IP family utilities, netlink conntrack, Linux `unix` protocol constants, and backend hostport managers. This is the main `HostPortManager` implementation callers should use when hostports are enabled.

## Risks And Edge Cases
IPv6 support is optional; IPv6 Add fails if no IPv6 backend is present. HostIP-family filtering can drop mappings silently. `HostPort <= 0` mappings are ignored. UDP conntrack cleanup failures are logged but not returned. Remove aggregates backend errors into a newline-joined error string but ignores iptables errors when nftables exists.

## Test Signals
`meta_hostport_manager_test.go` covers iptables-only, nftables-only, both-backend preference, legacy iptables cleanup while using nftables, and IPv4-only manager behavior.
