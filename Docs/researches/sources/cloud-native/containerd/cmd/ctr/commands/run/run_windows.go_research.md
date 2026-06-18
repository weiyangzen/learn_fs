<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_windows.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run_windows.go

## Purpose
Windows container construction for `ctr run`, including Windows/LCOW spec setup, snapshots, networking, isolation, resource limits, devices, and runtime options.

## Important APIs, Types, And Functions
Defines Windows `platformRunFlags`, `NewContainer`, and Windows `getNetNSPath`.

## Control Flow
Chooses default Windows or LCOW spec based on snapshotter, applies env/mount/process/user/tty settings, unpacks the image, creates a snapshot, rejects host networking, optionally creates a netns for CNI, applies Hyper-V isolation and Windows CPU/memory/device options, and creates the container with runhcs runtime options when selected.

## State And Persistence
Persists container metadata, snapshots, unpacked image layers, and optional Windows network namespace paths/extensions.

## Dependencies And Integration Points
Uses hcsshim runhcs options, containerd image/snapshot/diff APIs, Windows OCI helpers, netns, console sizing, and runtime flags.

## Risks And Test Signals
CNI namespace creation must be cleaned by task teardown paths; devices require strict `IDType://ID` format. No direct tests in this file. Source size reviewed: 202 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_windows.go -->
