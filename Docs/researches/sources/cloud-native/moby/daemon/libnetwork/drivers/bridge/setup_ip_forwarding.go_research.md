<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding.go

## Purpose
Checks and configures host IPv4/IPv6 forwarding sysctls and optionally asks the firewaller to set a default FORWARD DROP policy when enabling forwarding.

## Important APIs, Types, And Functions
Constants name forwarding sysctls. `filterForwardDropper` abstracts `FilterForwardDrop`. `checkIPv4Forwarding`, `setupIPv4Forwarding`, `checkIPv6Forwarding`, `setupIPv6Forwarding`, and `configureIPForwarding` implement checks/writes.

## Control Flow
Check functions read sysctls and return user-facing errors if forwarding is disabled. Setup functions write `1` to the required sysctls, register rollback defers if they changed values, and call `FilterForwardDrop` only when forwarding was newly enabled and requested. Rollback resets sysctls to `0` if later setup fails.

## State And Persistence
State is host `/proc/sys/net/ipv4/ip_forward` and IPv6 `default`/`all` forwarding files. These are host-global and security-sensitive.

## Dependencies And Integration Points
Uses firewaller `IPVersion`, `os.ReadFile/WriteFile`, and logging. Called by daemon bridge setup when IP forwarding management is enabled or checked.

## Risks And Edge Cases
The duplicate zero-length read check is harmless but redundant. Partial failure after changing one IPv6 sysctl triggers rollback. Enabling forwarding without filter DROP can expose host routing depending on firewall rules.

## Test Signals
`setup_ip_forwarding_test.go` validates sysctl writes, firewaller callback family selection, and check errors when forwarding is disabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding.go -->
