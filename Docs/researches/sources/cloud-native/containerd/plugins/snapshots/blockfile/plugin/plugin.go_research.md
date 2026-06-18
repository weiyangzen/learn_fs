# sources/cloud-native/containerd/plugins/snapshots/blockfile/plugin/plugin.go

## Purpose
This file registers the blockfile snapshotter plugin.

## Important APIs, Types, And Functions
`Config` exposes `root_path`, `scratch_file`, `fs_type`, `mount_options`, and `recreate_scratch`. The snapshot plugin type is `plugins.SnapshotPlugin`, ID `blockfile`. Initialization sets default platform metadata, builds blockfile options, exports `plugins.SnapshotterRootDir`, and calls `blockfile.NewSnapshotter`.

## Control Flow
The plugin chooses the configured root path or plugin root property, translates non-empty config fields to options, always appends `WithRecreateScratch`, and returns the snapshotter.

## State And Persistence
The configured root contains blockfile metadata and snapshot images. The plugin itself only exports root metadata.

## Dependencies And Integration Points
It integrates blockfile snapshotter construction with containerd plugin registration and platform metadata.

## Risks
Without a scratch file or preexisting scratch image, the underlying snapshotter skips plugin initialization. Configuration type mismatches fail startup. No platform guard is present here, so support depends on runtime mount behavior.

## Test Signals
No direct plugin test is included. Blockfile snapshotter suite validates the implementation, while daemon plugin tests would validate config wiring.
