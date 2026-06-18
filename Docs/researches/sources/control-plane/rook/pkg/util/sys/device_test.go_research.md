# sources/control-plane/rook/pkg/util/sys/device_test.go

## Purpose
This file tests block-device parsing and classification helpers.

## Important APIs, Types, and Functions
Fixtures model `udevadm` and `lsblk` output. `TestFindUUID()` validates GPT UUID parsing. `TestParseFileSystem()` and `TestParseUdevInfo()` parse udev data. `TestGetPartitions()` uses a mock executor to simulate several `lsblk`/`udevadm` sequences. `TestListDevicesChildListDevicesChild()` checks child splitting. `TestGetDiskDeviceType()` and `TestGetDiskDeviceClass()` check classification and env override.

## Control Flow, State, and Persistence
Tests are pure except for `t.Setenv()` and mock executor callback state. `TestGetPartitions()` uses a run counter to return different outputs across sequential command calls.

## Dependencies and Integration Points
It depends on `util/exec/test.MockExecutor`, testify, and sys parsers. It protects host-device discovery logic without requiring real disks.

## Risks
The run-counter mock makes `TestGetPartitions()` order-sensitive and hard to extend. Command failure paths, malformed JSON from ceph-volume, `GetLVName()`, and availability checks are not covered.

## Test Signals
Signals include preserving partition labels from udev, calculating unused space, treating Ceph LVM names as partitions, child device splitting, rotational/nvme/ssd classification, and crush class env override.
