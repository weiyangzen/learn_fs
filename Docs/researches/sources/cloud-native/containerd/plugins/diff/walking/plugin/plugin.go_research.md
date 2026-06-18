# sources/cloud-native/containerd/plugins/diff/walking/plugin/plugin.go

## Purpose
Registers the generic walking diff plugin, combining the walking comparer with a filesystem applier.

## Important APIs, Types, And Functions
`init` registers the `walking` diff plugin. `diffPlugin` embeds `diff.Comparer` and `diff.Applier`.

## Control Flow
Startup gets metadata DB, optionally gets the mount manager, advertises the default platform, obtains the content store, builds `walking.NewWalkingDiff`, builds `apply.NewFileSystemApplierWithMountManager`, and returns the combined plugin.

## State And Persistence
No direct persistence. It uses the content store from metadata and optionally the mount manager for apply operations.

## Dependencies And Integration Points
Depends on metadata, optional mount manager, core diff apply, plugin registry, and platforms. The diff service selects it according to platform-specific default ordering.

## Risks
Mount manager errors other than plugin-not-found are startup-fatal. Apply behavior changes depending on whether a mount manager is available.

## Test Signals
No direct tests. Walking differ and filesystem applier are exercised by diff/apply integration tests.
