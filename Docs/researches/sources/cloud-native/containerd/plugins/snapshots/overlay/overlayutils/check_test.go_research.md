<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check_test.go

## Purpose
Benchmarks and validates overlay backing-filesystem support detection against temporary loopback filesystems.

## Important APIs, Types, And Functions
`testOverlaySupported` creates a loopback device, formats it, mounts it, and runs `Supported`. Benchmarks cover ext4, XFS with `ftype=0`, XFS with `ftype=1`, and FAT.

## Control Flow
The helper requires root, allocates a 100 MiB loopback device, runs the selected `mkfs`, mounts it, invokes `Supported`, and checks whether success matches the expected result. When called as a benchmark, it repeats only the support check inside the timer.

## State And Persistence
Temporary mount points and loopback devices are cleaned up with deferred unmount and close. Formatting/mount failures skip rather than fail.

## Dependencies And Integration Points
Depends on external mkfs tools, mount command availability, root privileges, continuity loopback helpers, and `pkg/testutil`.

## Risks And Edge Cases
These are benchmarks, not normal `Test*` tests, so routine CI may not run them. Environment tool availability controls coverage.

## Test Signals
Provides focused evidence that `Supported` accepts ext4 and XFS ftype=1 and rejects XFS ftype=0 and FAT.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check_test.go -->
