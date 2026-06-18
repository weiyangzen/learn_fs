# sources/cloud-native/moby/daemon/reload_test.go

## Purpose
Tests daemon reload behavior for labels, registry mirrors, insecure registries, preservation of unrelated fields, network diagnostics, and copied `netip.Addr` values.

## Important APIs, Types, And Functions
`muteLogs` lowers log noise. `newDaemonForReloadT` constructs a minimal daemon with image and registry services. Tests call `Daemon.Reload`, `registry.NewService`, `ServiceConfig`, `daemon.networkOptions`, and libnetwork diagnostic methods.

## Control Flow
Tests build initial daemon configs, prepare reload configs with `ValuesSet`, invoke `Reload`, and assert new live config or registry service state. Invalid mirror tests expect reload errors; valid mirror/insecure registry tests inspect normalized service config. The diagnostic test, run only as root, repeatedly enables/disables diagnostic ports.

## State And Persistence
State is in-memory daemon config and service objects. The network diagnostic test creates a real libnetwork controller rooted in a temporary directory and mutates diagnostic server state.

## Dependencies And Integration Points
Depends on daemon config types, image service, registry service, libnetwork, copystructure, `netip`, and gotest assertions. It validates the integration between reload hooks and downstream services.

## Risks And Edge Cases
Some tests use manually populated `ValuesSet`; reload behavior depends on those flags. The diagnostic test requires root and is skipped otherwise. Registry tests inspect merged CIDR/index config rather than every TLS side effect.

## Test Signals
Passing tests confirm reload updates selected fields, leaves unmentioned fields unchanged, normalizes mirrors, replaces insecure registries exactly once, and preserves DNS/host gateway `netip.Addr` values.
