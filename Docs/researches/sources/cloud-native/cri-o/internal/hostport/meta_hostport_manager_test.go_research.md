# sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager_test.go

## Purpose
Tests the meta hostport manager's backend selection, dual-stack routing, nftables preference, migration cleanup, and IPv4-only behavior.

## Important APIs, Types, And Functions
- Exercises `newMetaHostportManagerInternal`, `HostPortManager.Add`, and `HostPortManager.Remove`.
- Uses fake iptables backends and `knftables.Fake` backends.
- Reuses `checkIPTablesRules`, `checkNFTablesElements`, and shared IPv4/IPv6 test cases.

## Control Flow
The file builds an interleaved list of IPv4 and IPv6 cases. Separate tests construct managers with only iptables, only nftables, both backends, and only IPv4 support. The migration test first creates legacy iptables rules, rebuilds a manager with nftables also available, verifies new Add operations use nftables without disturbing legacy iptables rules, then verifies Remove clears both backends.

## State And Persistence
Mutates fake iptables and fake nftables state to model persistent kernel rules across manager restarts. The migration test intentionally carries fake iptables state across manager instances.

## Dependencies And Integration Points
Validates the integration contract between meta manager and both backends. Uses Kubernetes IP family utilities to decide expected IPv6 failure in IPv4-only mode.

## Risks And Edge Cases
The tests do not verify UDP conntrack cleanup because the real netlink function is not faked here. They rely on backend expected outputs and stable sandbox hash/chain derivation.

## Test Signals
Very strong signal for upgrade/downgrade safety: CRI-O can switch to nftables for new hostports while still removing old iptables hostports.
