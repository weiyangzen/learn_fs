# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux.go

## Purpose
Linux-specific helpers for inferring host-reserved address prefixes and generating non-conflicting network interface names.

## Important APIs, Types, And Functions
`InferReservedNetworks(v6 bool)` combines nameserver prefixes from `resolv.conf` with IPv4 on-link routes. `tryGetNameserversAsPrefix` parses resolver config and converts nameservers to host prefixes. `queryOnLinkRoutes` returns IPv4 link-scope route destinations from netlink. `GenerateIfaceName` tries up to three random names and checks link existence through `nlwrap`.

## Control Flow
`InferReservedNetworks` best-effort reads `resolvconf.Path()`, filters nameserver prefixes by address family, appends on-link IPv4 routes for IPv4 requests, sorts with `netiputil.PrefixCompare`, and returns the result. Interface generation loops three times, returning the first name for which netlink reports `LinkNotFoundError`.

## State And Persistence
No persistent state. It reads current host `/etc/resolv.conf` and netlink route/link state.

## Dependencies And Integration Points
Called by `network.go` IPAM allocation for non-global networks to avoid selecting subnets likely in use by the host. Depends on `resolvconf`, `ns.NlHandle`, `nlwrap`, and vishvananda netlink.

## Risks
The reservation heuristic is intentionally incomplete and best-effort; users may still need daemon `default-address-pools` tuning. Route listing failures silently produce fewer exclusions. `GenerateIfaceName` has a small retry count and can fail under repeated collisions or netlink errors.

## Test Signals
`utils_linux_test.go` verifies resolver parsing, random name constraints, random MAC generation, and route-scope filtering in an isolated test namespace.
