# sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device_test.go

## Purpose
This file integration-tests devmapper pool device orchestration on loopback-backed thin pools.

## Important APIs, Types, And Functions
`TestPoolDevice` creates a thin pool, constructs `PoolDevice`, creates thin devices, formats ext4, writes data, creates a snapshot, verifies snapshot isolation, deactivates/removes devices, and tests rollback activation. `TestPoolDeviceMarkFaulty` checks state reconciliation. Helpers create loop devices, mkfs ext4, and mount devices.

## Control Flow
The main test executes an ordered scenario because later operations depend on earlier devices. It uses `mount.WithTempMount` to write/read data. Cleanup removes the pool and detaches loop devices.

## State And Persistence
Tests create real kernel device-mapper devices and temporary metadata databases under temp dirs.

## Dependencies And Integration Points
They require root, dmsetup, mkfs.ext4, loop devices, mount helpers, docker units, and logging configuration.

## Risks
Environment failures can leave kernel devices if cleanup fails. Coverage is realistic but expensive and not suitable for unprivileged CI.

## Test Signals
Passing tests validate pool creation, device ID metadata, snapshot correctness, usage reporting after mkfs, deactivation, removal, and recovery marking.
