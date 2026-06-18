<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup.go

## Purpose
Provides a small ordered setup pipeline for applying bridge network setup steps with OpenTelemetry spans.

## Important APIs, Types, And Functions
`setupStep` stores a name and `stepFn`. `stepFn` accepts `networkConfiguration` and `bridgeInterface`. `bridgeSetup` stores config, bridge, and queued steps. `newBridgeSetup`, `apply`, and `queueStep` manage the pipeline.

## Control Flow
Callers queue named setup functions, then `apply` iterates in order. Each step runs inside a span named from the bridge span prefix and step name, records success/error, ends the span, and stops on first error.

## State And Persistence
Only in-memory step slices are held. Effects are produced by the queued functions: netlink devices, addresses, sysctls, and firewall state.

## Dependencies And Integration Points
Uses `context`, OpenTelemetry, and `otelutil.RecordStatus`. It is the orchestration layer for setup files such as device, IPv4/IPv6, forwarding, and bridge netfiltering.

## Risks And Edge Cases
Step order is semantically important and errors stop later setup, so queued order must match bridge lifecycle requirements. The current `stepFn` does not accept context; `apply` creates a child context for future compatibility.

## Test Signals
No direct tests in this subset; behavior is exercised indirectly through network creation tests that depend on successful setup sequencing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup.go -->
