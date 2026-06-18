# sources/distributed-fs/ceph-client/samples/vfs/samples-vfs.h

## Purpose
`samples-vfs.h` provides compatibility definitions for VFS sample programs that need new mount namespace, `statmount()`, `listmount()`, and mount attribute UAPI declarations before libc or installed headers may expose them.

## APIs, Types, And Functions
The header defines `die_errno()`, `struct statmount`, `struct mnt_id_req`, and `struct mnt_ns_info`. It supplies syscall numbers, request sizes, namespace ioctl numbers, mount ID constants, `STATMOUNT_*` masks, `STATX_MNT_ID_UNIQUE`, `MOUNT_ATTR_*`, and selected `MS_*` flags when absent.

## Control Flow
There is no executable control flow. Including programs use the structures to build raw syscall/ioctl requests and interpret returned variable-length strings through offsets into `statmount.str[]`.

## State And Persistence
No persistent state exists. Structure layout is ABI-significant for user/kernel exchange, particularly versioned `mnt_id_req` sizes and trailing string offsets.

## Dependencies And Integration Points
It depends on `<linux/types.h>`, `<sys/ioctl.h>`, and syscall/ioctl conventions. It is shared by `mountinfo.c` and `test-list-all-mounts.c` and bridges samples to evolving kernel UAPI.

## Risks And Test Signals
The main risk is layout or constant drift relative to current UAPI headers. Test signals include successful compilation against both old and new userspace headers and working `statmount`/`listmount` samples on kernels implementing these syscalls.
