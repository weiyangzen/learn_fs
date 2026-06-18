# sources/cloud-native/moby/integration/networking/etchosts_test.go

## Purpose
Validates container `/etc/hosts` generation and update behavior for IPv4/IPv6 and multi-network disconnect scenarios. It protects regressions where IPv6-disabled containers received IPv6 host entries or stale network aliases remained after disconnect.

## Important APIs, Types, And Functions
Uses daemon helpers with `--ipv6` and `--fixed-cidr-v6`, container helpers for sysctls, hostname, extra hosts, and network mode, plus `NetworkConnect` and `NetworkDisconnect`. Golden assertions compare exact `/etc/hosts` content for multi-network state transitions.

## Control Flow
`TestEtcHostsIpv6` starts an IPv6-enabled daemon and runs two containers: one default and one with `net.ipv6.conf.all.disable_ipv6=1`. It pings `::1` to confirm IPv6 availability, reads `/etc/hosts`, appends expected container self entries from inspect output, and compares exact text. `TestEtcHostsDisconnect` creates bridge and ipvlan dual-stack networks, starts a container with hostname and extra hosts, connects/disconnects networks in different orders, and compares five golden states.

## State And Persistence Behavior
The file tests generated container filesystem state, specifically `/etc/hosts` content as endpoint attachments change. It confirms disconnect removes only entries for the detached network while preserving extra hosts and remaining network entries. No daemon restart persistence is exercised.

## Dependencies And Integration Points
Depends on Linux container filesystem generation, bridge and ipvlan network drivers, Docker endpoint bookkeeping, golden files under `integration/networking/testdata`, and BusyBox `cat`/`ping`.

## Risks
Exact text comparison is sensitive to line ordering, hostname formatting, and generated address ordering. The disconnect test deliberately avoids initial multi-network creation because generated entry order may be nondeterministic.

## Test Signals
Signals are precise: IPv6 ping exit code, exact `/etc/hosts` content for enabled/disabled IPv6, and five golden snapshots across connect/disconnect ordering.
