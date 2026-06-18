# sources/cloud-native/containerd/defaults/defaults_unix_other.go

## Purpose
This file provides defaults for Unix platforms other than Linux and Darwin.

## Important APIs, Types, and Functions
Constants define default socket/debug/FIFO paths under `/var/run/containerd`, default snapshotter `native`, transient state dir `/var/run/containerd`, and differ `walking`.

## Control Flow
No executable flow.

## State and Persistence
State is transient under `/var/run`; persistent root/config come from shared Unix defaults.

## Dependencies and Integration Points
Build tag `unix && !linux && !darwin` combines with platform-specific runtime constants such as FreeBSD.

## Risks
`native` snapshotter is conservative but may differ in performance and semantics from overlay/erofs defaults.

## Test Signals
Platform build coverage validates symbol composition.
