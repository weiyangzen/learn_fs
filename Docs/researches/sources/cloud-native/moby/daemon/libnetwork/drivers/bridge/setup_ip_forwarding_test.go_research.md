<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding_test.go

## Purpose
Tests IP forwarding setup/check helpers and their interaction with the firewaller default-DROP callback.

## Important APIs, Types, And Functions
`ffDropper` records whether `FilterForwardDrop` was called for IPv4 or IPv6. Tests include `TestSetupIPForwarding`, `TestSetupIP6Forwarding`, `TestCheckForwarding`, and helper `setForwarding`.

## Control Flow
Tests run in isolated OS context, force forwarding sysctls to `0`, call setup with `wantFFD` true/false, assert callback state and sysctl contents, then verify check functions fail when disabled and pass when enabled.

## State And Persistence
State is temporary namespace/proc sysctl values for IPv4 and IPv6 forwarding. `setForwarding` writes all three sysctls used by the implementation.

## Dependencies And Integration Points
Uses `netnsutils`, `os`, `firewaller`, and `gotest.tools`. It directly validates `setup_ip_forwarding.go`.

## Risks And Edge Cases
Requires writable forwarding sysctls in the test namespace. Tests focus on success and disabled-check paths; they do not inject write failures to validate rollback defers.

## Test Signals
Passing tests signal correct sysctl enablement, correct IPv4/IPv6 callback dispatch, no callback when not requested, and clear error messages for disabled forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding_test.go -->
