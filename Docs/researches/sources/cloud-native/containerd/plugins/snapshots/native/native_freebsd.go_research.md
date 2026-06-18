<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_freebsd.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native_freebsd.go

## Purpose
Supplies FreeBSD-specific native snapshotter mount settings.

## Important APIs, Types, And Functions
Defines `mountType = "nullfs"` and an empty `defaultMountOptions`.

## Control Flow
No functions. The shared native snapshotter appends `ro` or `rw` to create FreeBSD nullfs mounts.

## State And Persistence
No state.

## Dependencies And Integration Points
Builds on FreeBSD and is consumed by `native.go`.

## Risks And Edge Cases
FreeBSD nullfs option semantics differ from Linux bind mounts, so behavior relies on the generic snapshotter suite catching mount/read/write regressions on FreeBSD.

## Test Signals
Covered indirectly by `TestNative` on FreeBSD.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_freebsd.go -->
