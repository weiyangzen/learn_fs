# sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup_test.go

## Purpose
This file integration-tests the dmsetup wrapper against real loopback-backed device-mapper devices.

## Important APIs, Types, And Functions
`TestDMSetup` creates data and metadata loop devices, then runs subtests for pool creation, pool reload, thin device creation, snapshot creation/deletion, activation, status, suspend/resume, discard, remove, and version. Helper `createLoopbackDevice` allocates loop devices.

## Control Flow
The test creates a thin pool, executes operations in order, asserts expected errno values for duplicate or invalid operations, and removes pool/devices at the end. Loop devices are detached in defers.

## State And Persistence
Temporary files are attached as loop devices, then used as devmapper data/metadata devices. Kernel device-mapper state is created and removed during the test.

## Dependencies And Integration Points
It requires root, `dmsetup`, blkdiscard behavior, loop devices, containerd mount helpers, docker units, and `testify`.

## Risks
Tests are highly environment-dependent and can leave devices behind if cleanup fails. They do not test all dmsetup output variants.

## Test Signals
Passing tests strongly validate command construction and parsing against the local kernel/tools combination.
