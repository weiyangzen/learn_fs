# sources/cloud-native/containerd/defaults/defaults_darwin.go

## Purpose
This Darwin-specific file defines default runtime, socket paths, FIFO path, snapshotter, state directory, and differ.

## Important APIs, Types, and Functions
Constants include `DefaultRuntime`, `DefaultAddress`, `DefaultDebugAddress`, `DefaultFIFODir`, `DefaultSnapshotter`, `DefaultStateDir`, and `DefaultDiffer`.

## Control Flow
No executable flow.

## State and Persistence
Paths point at `/var/run/containerd` transient locations. The default snapshotter/differ are `erofs` because Darwin lacks Linux mount support.

## Dependencies and Integration Points
Used by Darwin builds of clients and daemon defaults.

## Risks
Defaults affect out-of-the-box connectivity and storage behavior on Darwin; snapshotter choice is constrained by platform support.

## Test Signals
No direct tests in subset; platform builds validate symbol availability.
