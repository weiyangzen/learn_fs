# sources/control-plane/rook/pkg/util/sys/device.go

## Purpose
`device.go` discovers, classifies, parses, and evaluates local block devices for Rook/Ceph OSD provisioning.

## Important APIs, Types, and Functions
Constants define device types such as `disk`, `part`, `crypt`, `lvm`, `mpath`, and `loop`. Data types include `CephVolumeInventory`, `CephVolumeLVMList`, `Partition`, and `LocalDisk`. Discovery functions include `ListDevices()`, `GetDevicePartitions()`, `GetDeviceProperties()`, `GetDevicePropertiesFromPath()`, `GetUdevInfo()`, `GetDeviceFilesystems()`, `GetDiskUUID()`, `ListDevicesChild()`, and `IsDeviceEncrypted()`. Classification functions include `IsLV()`, `GetDiskDeviceType()`, `GetDiskDeviceClass()`, `CheckIfDeviceAvailable()`, and `GetLVName()`. Parsers include `parseUUID()`, `parseKeyValuePairString()`, `parseFS()`, and `parseUdevInfo()`.

## Control Flow, State, and Persistence
The file shells out through `exec.Executor` to `lsblk`, `udevadm`, `sgdisk`, `dmsetup`, and `ceph-volume`. It parses text or JSON output and returns in-memory structs. Availability checks select Ceph inventory or LVM list logic based on `IsLV()`.

## Dependencies and Integration Points
It depends on Rook exec abstraction, Google UUID parsing, Go `os/exec.LookPath`, environment variables for crush class override, and host storage tools. It integrates with OSD device discovery and provisioning.

## Risks
Parsing is mostly ad hoc and can break on spaces or unexpected quoting in `lsblk`/`udevadm` output. `CheckIfDeviceAvailable()` accepts `pvcBacked` but does not use it. Host command availability and permissions are required. `IsDeviceEncrypted()` compares exact output to `crypt`, so trailing newlines can affect results depending on executor trimming.

## Test Signals
`device_test.go` covers UUID parsing, filesystem parsing, partition parsing including LVM child names, child listing, disk type, and env override for device class. Ceph-volume availability, LV name parsing, encryption detection, and command failures have limited or no coverage.
