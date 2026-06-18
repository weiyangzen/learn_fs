# sources/cloud-native/moby/daemon/update.go

## Purpose
`update.go` updates container host/resource configuration and applies resource changes to running tasks.

## Important APIs, Types, And Functions
`ContainerUpdate` validates requested settings and returns warnings. `update` persists host config, updates restart policy monitor, and calls containerd task `UpdateResources` for running containers. `errCannotUpdate` wraps errors with container context.

## Control Flow
Validation runs before container lookup/update. `update` backs up `HostConfig`, sets a deferred rollback flag, locks the container, rejects removal/dead state, calls `UpdateContainer`, checkpoints, unlocks, updates monitor if restart policy changed, logs an update event, gets a running task unless stopped/restarting, converts resources to containerd resources, and applies them. On failure after mutation it restores the old host config and checkpoints if the container is still valid.

## State And Persistence
Persists `HostConfig` changes, restart monitor policy, container checkpoints, resource limits in the running containerd task, and update events.

## Dependencies And Integration Points
Integrates daemon config validation, container state/host config mutation, containerd resource conversion/update, restart monitor, errdefs, and events.

## Risks
Rollback is critical because config persistence can succeed before runtime resource update fails. Stopped/restarting containers keep only persisted config for next start. Containerd resource update errors are wrapped as system errors.

## Test Signals
Container update integration tests cover validation warnings, stopped/running update behavior, restart policy changes, and resource update failures.
