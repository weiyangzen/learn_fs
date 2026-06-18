# sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs_test.go

## Purpose
This file provides root-gated integration tests for the btrfs snapshotter.

## Important APIs, Types, And Functions
`boltSnapshotter` creates a loopback device, formats it with `mkfs.btrfs`, mounts it, and returns a snapshotter factory. `TestBtrfs` runs `testsuite.SnapshotterSuite`. `TestBtrfsMounts` verifies generated btrfs mounts and basic parent/child content behavior.

## Control Flow
Tests skip when `mkfs.btrfs` or the btrfs kernel module is unavailable. The factory retries snapshotter initialization after remounting if btrfs mount detection races. Cleanup closes the snapshotter, unmounts, and closes the loopback device.

## State And Persistence
All state lives on temporary loopback files and temporary mount roots. Subvolumes are created and removed during test lifecycle.

## Dependencies And Integration Points
The tests depend on root privileges, btrfs kernel support, mkfs tooling, loopback helpers, containerd mount helpers, and snapshotter testsuite.

## Risks
Environment sensitivity is high. The tests do not exercise all rollback paths or quota/usage edge cases, but they do catch core mount and content inheritance behavior.

## Test Signals
Passing tests indicate the snapshotter conforms to generic lifecycle expectations and returns usable `subvolid` mount specs.
