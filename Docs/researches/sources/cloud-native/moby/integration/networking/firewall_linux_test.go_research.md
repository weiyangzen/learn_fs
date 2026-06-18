# sources/cloud-native/moby/integration/networking/firewall_linux_test.go

## Purpose
Checks that daemon `GET /info` exposes the expected Linux firewall backend metadata and that older API versions omit the field for compatibility.

## Important APIs, Types, And Functions
Uses `daemon.New`, `StartWithBusybox`, `client.Info`, `request.NewAPIClient` with API version `1.48`, `networking.FirewalldRunning`, and `DOCKER_FIREWALL_BACKEND`. The expected default backend is the local constant `defaultFirewallBackend = "iptables"`.

## Control Flow
The test starts a daemon, determines expected driver from `DOCKER_FIREWALL_BACKEND`, appends `+firewalld` when non-rootless and firewalld is running, then calls `Info` and asserts `Info.FirewallBackend` is present with the expected driver. A subtest creates an API 1.48 client and asserts the same field is nil.

## State And Persistence Behavior
No persistent network state is mutated beyond daemon startup. The test reads runtime daemon/firewall state and compatibility serialization behavior.

## Dependencies And Integration Points
Integrates Docker API version negotiation, daemon info response shape, rootless detection, firewalld detection, and configured firewall backend selection.

## Risks
Environment variables and firewalld state directly affect expectations. Backend naming changes or API version gates would break this test even if firewall behavior still works.

## Test Signals
Main signal is the exact `Info.FirewallBackend.Driver` match and presence/absence of the field by API version.
