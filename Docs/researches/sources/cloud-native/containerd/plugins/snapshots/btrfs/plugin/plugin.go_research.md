# sources/cloud-native/containerd/plugins/snapshots/btrfs/plugin/plugin.go

## Purpose
This file registers the btrfs snapshotter plugin for Linux/cgo builds.

## Important APIs, Types, And Functions
`Config` exposes `root_path`. The plugin type is `plugins.SnapshotPlugin`, ID `btrfs`, and initialization sets `ic.Meta.Platforms`, chooses the root path, exports `plugins.SnapshotterRootDir`, and calls `btrfs.NewSnapshotter`.

## Control Flow
The plugin uses the configured root when present, otherwise the plugin root property. Invalid config type returns an error.

## State And Persistence
Persistent state is created by `btrfs.NewSnapshotter` under the selected root.

## Dependencies And Integration Points
It integrates plugin registry, platform metadata, and the btrfs snapshotter implementation.

## Risks
Initialization skips or fails if the root is not on btrfs or system support is missing. Build tags exclude non-Linux, no-cgo, or `no_btrfs` builds.

## Test Signals
No direct plugin tests are included. Snapshotter integration tests validate the implementation behind the plugin.
