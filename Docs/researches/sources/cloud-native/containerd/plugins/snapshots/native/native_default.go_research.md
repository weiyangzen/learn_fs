<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_default.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native_default.go

## Purpose
Supplies default native snapshotter mount settings for all non-FreeBSD platforms.

## Important APIs, Types, And Functions
Defines `mountType = "bind"` and `defaultMountOptions = []string{"rbind"}`.

## Control Flow
No functions. `native.go` appends `ro` or `rw` to these defaults when returning mounts.

## State And Persistence
No state.

## Dependencies And Integration Points
Build-tagged `!freebsd`; consumed by `snapshotter.mounts`.

## Risks And Edge Cases
Assumes recursive bind mounts are the correct native representation on non-FreeBSD Unix-like systems. Windows is skipped by tests and does not implement native snapshotter behavior.

## Test Signals
Covered indirectly by `TestNative` and the snapshotter suite on Linux and other non-FreeBSD platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_default.go -->
