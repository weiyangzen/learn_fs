<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/health.go -->
# sources/cloud-native/moby/daemon/container/health.go

## Purpose
Wraps API health state with locking and monitor stop-channel lifecycle.

## Important APIs, Types, And Functions
`Health`, `String`, `Status`, `SetStatus`, `OpenMonitorChannel`, and `CloseMonitorChannel`.

## Control Flow
Status reads/writes are mutex-protected. Empty status defaults to unhealthy. Opening a monitor channel succeeds only once; closing it closes the channel, clears it, and marks health unhealthy for compatibility.

## State And Persistence Behavior
Health embeds API health data that may be serialized through container state. The stop channel is runtime-only.

## Dependencies And Integration Points
Uses container API health status constants and containerd logging. Consumed by container state stringification and health monitor code.

## Risks And Test Signals
Risks include defaulting not-yet-setup health to unhealthy and monitor close changing persisted status. Healthcheck integration tests are expected signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/health.go -->
