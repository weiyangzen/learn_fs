# sources/distributed-fs/ceph-client/samples/vfs/test-fsmount.c

## Purpose
`test-fsmount.c` demonstrates the fd-based mount API by creating an AFS superblock with `fsopen()`/`fsconfig()`, converting it to a detached mount with `fsmount()`, and attaching it at `/mnt` with `move_mount()`.

## APIs, Types, And Functions
It defines raw syscall wrappers for `fsopen`, `fsmount`, `fsconfig`, and `move_mount`. `check_messages()` drains fs context diagnostic messages, `mount_error()` reports them before exiting, and `E_fsconfig` wraps configuration failures.

## Control Flow
`main()` opens an AFS fs context, sets the `source` string to a public AFS cell, issues `FSCONFIG_CMD_CREATE`, calls `fsmount()` with read-only mount attributes, closes the context fd, and moves the detached mount to `/mnt` using `MOVE_MOUNT_F_EMPTY_PATH`.

## State And Persistence
The program creates kernel fs-context and mount file descriptors. It can persistently change the system mount table by attaching at `/mnt`; cleanup is external.

## Dependencies And Integration Points
It depends on recent fd-based mount syscalls, AFS filesystem support, network reachability for the sample source, privileges to mount, and `/mnt` availability. It integrates with the VFS mount API and fs-context diagnostic stream.

## Risks And Test Signals
Risks include requiring elevated privileges, mutating `/mnt`, relying on public AFS availability, and failing on kernels without syscall numbers. Test signals are successful mount attachment, diagnostic messages for invalid fsconfig/fsmount, and visible read-only AFS mount in mountinfo.
