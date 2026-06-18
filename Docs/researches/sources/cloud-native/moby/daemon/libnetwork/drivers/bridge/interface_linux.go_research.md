<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux.go

## Purpose
Models the Linux bridge interface managed by the driver and handles bridge discovery, address listing, and IPv6 address programming.

## Important APIs, Types, And Functions
`DefaultBridgeName` is `docker0`. `bridgeInterface` stores the netlink link, configured IPv4/IPv6 bridge prefixes, gateway IPs, and `nlwrap.Handle`. `newInterface` resolves an existing bridge by name and defaults an empty name to `docker0`. `exists` reports whether a link was found. `addresses` lists v4/v6 addresses. `programIPv6Addresses` reconciles configured IPv6 address state onto the bridge.

## Control Flow
`newInterface` looks up `config.BridgeName`, accepts missing links, and rejects existing non-bridge links. IPv6 programming stores desired state, converts the network to `netip.Prefix`, lists existing IPv6 addresses, removes unexpected non-multicast and non-standard link-local addresses, and finally calls `AddrReplace` with `IFA_F_NODAD`.

## State And Persistence
State is kernel netlink state plus cached fields on `bridgeInterface`. The code intentionally preserves standard link-local and multicast addresses and avoids removing/readding the same IPv6 address on live-restore to reduce traffic disruption.

## Dependencies And Integration Points
Uses `nlwrap`, `netlink`, `netiputil`, `errdefs`, and containerd logging. Called by bridge setup and network creation paths before IPv4/IPv6 gateway and firewall setup.

## Risks And Edge Cases
Existing non-bridge interfaces with the requested name are fatal. Prefix-length changes on an existing address are not actually reflected by `AddrReplace`, a documented cosmetic limitation. The code must avoid deleting kernel link-local addresses that keep IPv6 neighbor discovery functional.

## Test Signals
`interface_linux_test.go` covers default naming, absent interface address listing, v4/v6 address listing, link-local preservation, nonstandard link-local replacement, multicast preservation, and prefix shrink behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux.go -->
