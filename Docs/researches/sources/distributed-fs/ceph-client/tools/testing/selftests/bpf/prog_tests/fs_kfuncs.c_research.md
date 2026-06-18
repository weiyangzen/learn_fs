
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fs_kfuncs.c

## Purpose

`fs_kfuncs.c` validates filesystem-related BPF kfuncs for reading, setting/removing xattrs, and fs-verity operations through LSM hooks.

## Important APIs, Types, and Functions

The test uses `test_get_xattr.skel.h`, `test_set_remove_xattr.skel.h`, and `test_fsverity.skel.h`, plus Linux xattr syscalls and `linux/fsverity.h`. It creates `/tmp/test_progs_fs_kfuncs`, triggers `security_inode_getxattr`, validates `security.bpf.*` xattrs, and exercises fs-verity ioctls through skeleton-controlled BSS/data/rodata fields.

## Control Flow and Data Flow

`test_get_xattr()` creates a file, sets a named xattr, attaches an LSM BPF program for the current PID, calls `getxattr()`, and checks whether BPF observed file/dentry xattr values and optionally denied access. The set/remove path creates a file, seeds `security.bpf.foo`, attaches programs that modify `security.bpf.bar`, and validates set, replacement, and removal from user space. Fs-verity subtests create file content, attach the skeleton, invoke fs-verity operations, and compare BPF-observed digest/signature behavior.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is temporary file metadata, xattrs, fs-verity state, and skeleton BSS counters. Dependencies include `/tmp` filesystem xattr support, LSM BPF, fs-verity kernel/filesystem support for relevant paths, and permission to manipulate security xattrs. Integration points are VFS/LSM hooks and filesystem kfunc ABI. Risks are filesystem-specific unsupported features, cleanup after partial xattr setup, and errno differences. Test signals are skip on `EOPNOTSUPP`, expected `getxattr()` return/errno, BSS flags for file/dentry discovery, and matching/removal of xattr values.
