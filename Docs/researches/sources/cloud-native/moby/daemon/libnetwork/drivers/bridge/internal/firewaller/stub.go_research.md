<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/stub.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/stub.go

## Purpose
Provides an in-memory firewaller implementation for unit tests, recording requested networks, endpoints, ports, and links without touching host firewall state.

## Important APIs, Types, And Functions
`NewStubFirewaller` constructs `StubFirewaller` with a `Networks` map. `NewNetwork` creates a `StubFirewallerNetwork`. Network methods implement `ReapplyNetworkLevelRules`, `DelNetworkLevelRules`, `AddEndpoint`, `DelEndpoint`, `AddPorts`, `DelPorts`, `AddLink`, and `DelLink`. Helpers `PortExists`, `LinkExists`, and `matchLink` support assertions.

## Control Flow
Tests install the stub through `useStubFirewaller`; bridge operations then mutate in-memory maps/slices. Deleting network-level rules removes the network only when endpoints, ports, and links have already been cleared.

## State And Persistence
State is in memory only. It records endpoint address pairs, copied port bindings, and cloned legacy link port lists. It deliberately tracks networks even though production firewallers rely on the bridge driver to own network objects.

## Dependencies And Integration Points
Depends on `types`, `netip`, and `slices`. Integrated by bridge lifecycle, link, and port mapping tests to validate driver behavior independently of iptables/nftables availability.

## Risks And Edge Cases
The stub is stricter than some production backends about deletion ordering; that is useful for driver tests but may not model reload-tolerant behavior. `AddPorts` ignores duplicate ports, matching idempotent firewall intent.

## Test Signals
Bridge tests use `PortExists` and `LinkExists` to assert port/link programming and verify network entries are created and removed as driver networks come and go.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/stub.go -->
