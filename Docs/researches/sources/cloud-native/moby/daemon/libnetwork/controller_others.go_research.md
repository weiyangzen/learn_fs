<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_others.go -->
# sources/cloud-native/moby/daemon/libnetwork/controller_others.go

## Purpose
Non-Linux stubs for controller firewall and OSL sandbox functionality.

## Important APIs, Types, And Functions
`FirewallBackend` returns nil, `enabledIptablesVersions` returns nil, and `setupOSLSandbox` is a no-op.

## Control Flow
These methods intentionally do nothing on non-Linux builds.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Allows common controller code to compile on platforms without Linux iptables/nftables/OSL namespace behavior.

## Risks And Edge Cases
Callers must tolerate nil firewall info and no OSL sandbox setup on non-Linux.

## Test Signals
Cross-platform build and non-Linux controller tests are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_others.go -->
