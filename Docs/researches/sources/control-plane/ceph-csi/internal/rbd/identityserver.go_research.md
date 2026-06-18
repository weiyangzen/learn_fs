# sources/control-plane/ceph-csi/internal/rbd/identityserver.go

## Purpose
Customizes the RBD CSI identity service by reporting plugin capabilities that depend on both static driver behavior and runtime librbd feature support.

## Important APIs, Types, And Functions
`IdentityServer` embeds the common default identity server. `GetPluginCapabilities` returns controller service, online volume expansion, and volume accessibility constraints by default, then conditionally adds group-controller service and snapshot-metadata service capabilities.

## Control Flow
The method builds a base capability slice, calls `features.SupportsGroupSnapGetInfo` and appends group-controller capability if supported, then calls `features.SupportsRBDSnapDiffByID` and appends snapshot metadata capability if supported. Detection errors are logged as warnings but do not fail the identity RPC.

## State And Persistence
No state is persisted. Feature detection uses cached in-memory state in the `features` package.

## Dependencies And Integration Points
Depends on CSI protobufs, `csicommon.DefaultIdentityServer`, feature detection, and logging. The advertised capabilities should match controller services registered by `driver.go`; mismatches can cause sidecars to call unsupported RPCs or miss available features.

## Risks And Test Signals
Risks include capability drift between identity and driver startup, runtime symbol detection differences, and silently degraded capability advertisement when detection errors are only logged. There are no direct tests for this file in the subset.
