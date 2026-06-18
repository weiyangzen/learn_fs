# sources/cloud-native/moby/daemon/libnetwork/iptables/conntrack.go

## Purpose
Deletes Linux conntrack state associated with container IP addresses or published ports so stale NAT/connection entries do not outlive network changes.

## Important APIs, Types, And Functions
- `checkConntrackProgrammable` verifies the netlink handle supports `NETLINK_NETFILTER`.
- `DeleteConntrackEntries` purges flows by IPv4/IPv6 container IP lists.
- `DeleteConntrackEntriesByPort` purges flows matching protocol, destination port, and optional host IP.
- `purgeConntrackState` deletes NAT-any-IP conntrack entries for one address/family.

## Control Flow
Both public functions return early for empty inputs, check netfilter support, then iterate targets. Per-target filter construction or deletion failures are logged and skipped so one bad entry does not abort the whole cleanup. Port cleanup queries both IPv4 and IPv6 families for each binding.

## State And Persistence
Effects are external kernel conntrack table mutations through netlink. No Go state persists.

## Dependencies And Integration Points
Uses libnetwork `nlwrap.Handle`, `types.PortBinding`, vishvananda `netlink`, and Linux syscall constants. Called by networking code when endpoint/port mappings change.

## Risks
Filtering by NAT-any-IP or port can delete broader state than intended if assumptions about unique subnets or bindings are violated. Unspecified host IP intentionally skips destination-IP filter because real conntrack entries use concrete interface IPs. Errors after initial programmability check are warnings, not returned.

## Test Signals
No direct tests in this subset. Behavior is integration-sensitive and depends on kernel netfilter support.
