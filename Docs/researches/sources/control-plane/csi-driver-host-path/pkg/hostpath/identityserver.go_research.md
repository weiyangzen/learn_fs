# sources/control-plane/csi-driver-host-path/pkg/hostpath/identityserver.go

## Purpose
This file implements the CSI identity service for the hostpath driver. It reports plugin name/version, liveness probe readiness, and high-level plugin service capabilities.

## Important APIs, Types, And Functions
`GetPluginInfo` validates `DriverName` and `VendorVersion` and returns them. `Probe` returns an empty successful `ProbeResponse`. `GetPluginCapabilities` always advertises controller service and group controller service, conditionally advertises volume accessibility constraints when topology is enabled, and conditionally advertises snapshot metadata service when enabled.

## Control Flow
Identity RPCs do not lock shared state. They read configuration and build CSI protobuf responses. Missing driver name or vendor version produces `codes.Unavailable`.

## State, Persistence, And Dependencies
No persistent state is touched. Dependencies are CSI protobufs, gRPC status codes, context, and klog.

## Integration Points
Kubelet, sidecars, liveness probe, and CSI test tools call identity RPCs early to discover driver identity and services. Capability advertisement must align with gRPC server registration and feature flags in `Run`.

## Risks
Group controller service is always advertised because the server always registers it; deployments without group snapshot CRDs may still show the CSI capability. Snapshot metadata is advertised only when the optional server is registered. Empty vendor version in tests or builds causes identity failure.

## Test Signals
Tests should check configured and missing driver/version responses, topology capability toggling, snapshot metadata capability toggling, and a successful probe.
