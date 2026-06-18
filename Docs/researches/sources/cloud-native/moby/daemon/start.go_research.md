# sources/cloud-native/moby/daemon/start.go

## Purpose
`start.go` implements container start orchestration and cleanup for failed or completed setup.

## Important APIs, Types, And Functions
`validateState` rejects paused/running/removal/dead containers. `ContainerStart` validates checkpoint mode and host settings, then calls `containerStart`. `containerStart` mounts storage, initializes networking, creates OCI spec, creates/replaces containerd container/task, starts it, updates container state, events, metrics, and checkpoints. `Cleanup` releases containerd, network, mounts, exec commands, volumes, and attach context.

## Control Flow
Start obtains daemon config/container, validates state and settings, then under container lock performs setup with deferred rollback. On error it records state error/exit code, checkpoints, resets, cleans up, and auto-removes if configured. Successful flow mounts, creates network sandbox, sets up dirs/mounts, builds spec, resets restart manager, saves AppArmor config, resolves checkpoint, creates containerd container/task, initializes task networking, starts task, sets running state, starts health monitor, checkpoints, logs start event, and records metrics.

## State And Persistence
Persists container state checkpoints, runtime assignment, mounted rootfs/volumes/secrets, network sandbox allocation, containerd container/task state, health monitor state, events, and metrics.

## Dependencies And Integration Points
Integrates containerd client/container/task APIs, daemon config, image service, libcontainerd, OCI spec generation, networking, mount setup, health monitor, events, metrics, and OpenTelemetry tracing.

## Risks
Start has many rollback paths; missed cleanup leaks mounts, network sandboxes, containerd tasks, or auto-remove containers. Locks must cover container state mutations without blocking backend cleanup indefinitely. Context cancellation is intentionally ignored for some containerd cleanup/start calls to avoid stuck integration tests.

## Test Signals
Broad daemon/container lifecycle integration tests cover start success, invalid states, checkpoints, failed setup cleanup, auto-remove, health, and event emission.
