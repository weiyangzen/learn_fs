<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/controller_linux.go

## Purpose
Linux-specific controller support for firewall reporting, enabled iptables versions, and OSL sandbox setup.

## Important APIs, Types, And Functions
`FirewallBackend` returns Docker info firewall metadata, including iptables/nftables, firewalld reload timestamp, and userland proxy fields. `enabledIptablesVersions` reports IPv4/IPv6 settings. `getDefaultOSLSandbox` lazily creates a shared namespace. `setupOSLSandbox` creates or attaches an OSL namespace and applies OS tweaks.

## Control Flow
Firewall reporting checks nftables and firewalld runtime state. Sandbox setup uses the default namespace when requested, creates a new sandbox unless an external key is used, then invokes OSL tweak application inside the namespace and again outside for compatibility/performance.

## State And Persistence
Stores a lazily initialized default OSL namespace in the controller. OSL namespace creation affects runtime namespace files under configured exec root.

## Dependencies And Integration Points
Integrates with Docker system info, nftables, iptables/firewalld, OSL namespace implementation, and sandbox configuration.

## Risks And Edge Cases
If default namespace creation fails, the `sync.Once` is reset for retry. Applying OS tweaks twice is intentional but non-obvious. Firewall info combines backend and firewalld state into a string consumed by Docker info users.

## Test Signals
Linux sandbox tests, Docker info firewall assertions, and live-restore namespace behavior exercise this code.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_linux.go -->
