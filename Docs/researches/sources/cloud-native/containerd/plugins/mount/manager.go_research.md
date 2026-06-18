# sources/cloud-native/containerd/plugins/mount/manager.go

## Purpose
Registers the Bolt-backed mount manager plugin that tracks activated mounts and delegates type-specific mount handling.

## Important APIs, Types, And Functions
Plugin init gathers mount handlers, configures `manager.WithMountHandler` and allowed roots, opens `mounts.db`, creates `manager.NewManager`, optionally runs `Sync`, and registers metadata collectible resources.

## Control Flow
Startup loads metadata, optional mount handlers, creates a target directory under plugin state, permits the parent of the containerd root as an allowed root, opens a bbolt DB, constructs the manager, starts a readiness-gated background sync transaction when supported, registers mount resources for GC if the manager implements `metadata.Collector`, and returns it.

## State And Persistence
Persists mount activation metadata in `mounts.db` and creates target mount directories under `state/t`. Kernel mount state is reconciled by optional sync.

## Dependencies And Integration Points
Requires metadata and mount-handler plugins. Uses bbolt, metadata bolt transaction context, mount manager package, and metadata GC resource registration. The mounts service and walking applier can depend on it.

## Risks
Sync runs in a goroutine but daemon readiness waits through the registered callback. DB open/create failures prevent startup. Allowed-root policy is broad enough to include the containerd root parent.

## Test Signals
No direct tests in this subset; mount service and integration tests cover behavior.
