# sources/cloud-native/containerd/defaults/defaults_linux.go

## Purpose
This Linux-specific file defines default socket paths, runtime, snapshotter, state directory, FIFO directory, and differ.

## Important APIs, Types, and Functions
Defaults include `/run/containerd/containerd.sock`, `/run/containerd/debug.sock`, `/run/containerd/fifo`, runtime `io.containerd.runc.v2`, snapshotter `overlayfs`, state dir `/run/containerd`, and differ `walking`.

## Control Flow
No executable flow.

## State and Persistence
The state directory is transient under `/run`; persistent root/config come from Unix defaults. Snapshotter default influences persisted snapshot metadata and unpack behavior.

## Dependencies and Integration Points
Used by Linux clients, integration tests, pull unpack matching, and daemon configuration.

## Risks
Changing defaults is deployment-visible. `DefaultSnapshotter` is used by transfer unpack matching when no snapshotter is requested.

## Test Signals
Integration client `TestMain` uses this default unless `TEST_SNAPSHOTTER` overrides it.
