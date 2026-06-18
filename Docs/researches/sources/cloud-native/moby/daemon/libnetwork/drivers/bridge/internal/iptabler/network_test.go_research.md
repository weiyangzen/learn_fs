<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network_test.go

## Purpose
Provides focused tests for iptables network-level rule helpers and outgoing NAT/SNAT behavior.

## Important APIs, Types, And Functions
`TestProgramIPTable` checks `programChainRule` add/delete. `TestSetupIPChains` creates networks with varying masquerade and ICC. `TestSetupIP6TablesWithHostIPv4` covers an IPv6 setup regression with IPv4 host SNAT. `TestOutgoingNATRules` enumerates daemon/family/host-IP combinations and asserts expected MASQUERADE or SNAT rules.

## Control Flow
Tests create isolated namespaces, initialize `NewIptabler`, create `firewaller.NetworkConfig` values, call `NewNetwork`, then assert rule existence or delete network-level rules. NAT tests dump tables to logs for troubleshooting and compare explicit expected iptables rules.

## State And Persistence
Only namespace-local iptables state is modified. No repository state is changed except optional test logs.

## Dependencies And Integration Points
Uses `iptables`, `netnsutils`, `firewaller`, `netip`, and `gotest.tools`. It bridges low-level rule helpers with the `firewaller.Firewaller` interface.

## Risks And Edge Cases
Environment must support iptables in isolated namespaces. The NAT matrix guards against accidental SNAT/MASQUERADE when iptables/ip6tables or masquerading is disabled, and against IPv4 host SNAT leaking into IPv6 setup.

## Test Signals
Passing tests signal reliable rule insertion/removal and correct outgoing NAT selection for IPv4, IPv6, host-specific SNAT, disabled tables, and mixed-family configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network_test.go -->
