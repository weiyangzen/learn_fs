# sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter_test.go

## Purpose
This file integration-tests the devmapper snapshotter and selected filesystem formatting behavior.

## Important APIs, Types, And Functions
`TestSnapshotterSuite` runs the generic snapshotter suite and a devmapper usage test. `testUsage` checks active base usage and committed child usage after writing a 1 MB file. `TestMkfsExt4`, `TestMkfsExt4NonDefault`, `TestMkfsXfs`, and `TestMkfsXfsNonDefault` validate mkfs error wrapping. `TestMultipleXfsMounts` checks XFS layer creation/mount behavior. `createSnapshotter` creates loopback pool devices and cleanup functions.

## Control Flow
Tests require root, create loopback data and metadata devices, create a thin pool, instantiate the snapshotter, prepend pool cleanup to snapshotter cleanup functions, and run lifecycle operations.

## State And Persistence
Real loopback files, thin pools, thin devices, and metadata DBs are created under temporary roots.

## Dependencies And Integration Points
They rely on root, dmsetup, mkfs.ext4/mkfs.xfs, loop devices, mount helpers, snapshotter testsuite, namespaces, and continuity filesystem test appliers.

## Risks
High environment sensitivity and potential cleanup leakage if kernel/device operations fail. The mkfs tests assert error text for empty paths rather than successful formatting.

## Test Signals
Passing tests validate snapshotter conformance, usage accounting directionally, fs type labels/options, and XFS `nouuid` mount behavior.
