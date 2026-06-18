# sources/cloud-native/containers-storage/pkg/loopback/attach_loopback.go

Purpose: attaches a sparse backing file to an available Linux loop device.

Important APIs, types, and functions: errors `ErrAttachLoopbackDevice`, `ErrGetLoopbackBackingFile`, `ErrSetCapacity`; `stringToLoopName`, `getNextFreeLoopbackIndex`, `openNextAvailableLoopback`, `AttachLoopDevice`, `AttachLoopDeviceRO`, and `attachLoopDevice`.

Control flow: the code opens `/dev/loop-control`, asks for a free index, opens `/dev/loopN`, verifies it is a block device, calls `LOOP_SET_FD`, verifies backing device/inode, then sets loop status with autoclear. It loops around races where another process grabs a device or the kernel reports ENXIO/EBUSY.

State and persistence: persistent kernel state is the loop device association with the backing file. `LO_FLAGS_AUTOCLEAR` asks the kernel to detach on last close. The sparse file is opened temporarily; the returned loop `*os.File` is caller-owned.

Dependencies and integration points: depends on `errors`, `fmt`, `io/fs`, `os`, `syscall`, `logrus`, and `x/sys/unix`. It uses ioctl wrappers and constants from sibling files.

Risks and edge cases: requires Linux loop device permissions. Race handling is bounded to 1000 attempts. Read-only mode opens the backing file read-only but does not set `LO_FLAGS_READ_ONLY`, which may matter for strict RO expectations. Verification mismatch logs but does not fail.

Test signals: `attach_test.go` stress-tests concurrent attachment on Linux when sufficient privileges/devices exist.
