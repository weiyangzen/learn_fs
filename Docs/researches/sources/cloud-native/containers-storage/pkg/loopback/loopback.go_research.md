# sources/cloud-native/containers-storage/pkg/loopback/loopback.go

Purpose: provides Linux helpers for querying, resizing, and finding loop devices by backing file.

Important APIs, types, and functions: `getLoopbackBackingFile`, `SetCapacity`, and `FindLoopDeviceFor`.

Control flow: `getLoopbackBackingFile` calls `LOOP_GET_STATUS64` and returns backing device/inode. `SetCapacity` calls `LOOP_SET_CAPACITY`. `FindLoopDeviceFor` stats the backing file, scans `/dev/loop0`, `/dev/loop1`, and so on until first non-existent loop device, returning the open loop file whose backing device/inode matches.

State and persistence: interacts with kernel loop-device state. `SetCapacity` updates the kernel's view of the loop device size. `FindLoopDeviceFor` returns an open file descriptor that the caller must close.

Dependencies and integration points: depends on `fmt`, `os`, `syscall`, and `logrus`; uses ioctl wrappers from this package.

Risks and edge cases: scanning stops at the first missing `/dev/loopN`, so sparse loop numbering could miss later devices. Non-not-exist open errors are ignored. Returned matched loop file stays open.

Test signals: no direct requested test for `FindLoopDeviceFor` or `SetCapacity`; attach tests exercise backing-file status reads indirectly.
