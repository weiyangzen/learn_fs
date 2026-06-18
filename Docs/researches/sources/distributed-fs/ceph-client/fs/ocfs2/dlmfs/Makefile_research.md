# sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/Makefile` defines the build composition for the OCFS2 DLMFS kernel component. The source was read as a complete 4-line file.

## Important APIs, Types, and Functions

There are no C APIs or runtime types in this file. Its important build variables are `obj-$(CONFIG_OCFS2_FS) += ocfs2_dlmfs.o` and `ocfs2_dlmfs-objs := userdlm.o dlmfs.o`.

## Control Flow

There is no runtime control flow. At build time, enabling `CONFIG_OCFS2_FS` causes kbuild to build `ocfs2_dlmfs.o` from `userdlm.o` and `dlmfs.o`.

## State and Persistence Behavior

The file defines no runtime state and performs no persistence. It controls whether the DLMFS code is linked as part of the OCFS2 filesystem build.

## Dependencies and Integration Points

The Makefile ties `dlmfs.c` and `userdlm.c` into one object named `ocfs2_dlmfs.o`. That object provides the `ocfs2_dlmfs` filesystem type and the user-DLM wrapper layer for OCFS2 stackglue.

## Risks and Edge Cases

Build composition is small but important: omitting either object breaks symbol resolution because `dlmfs.c` calls `user_dlm_*()` helpers and exports `user_dlm_worker`, while `userdlm.c` depends on that workqueue and DLMFS inode structures from `userdlm.h`. Tying the object to `CONFIG_OCFS2_FS` means DLMFS availability follows OCFS2 rather than a separate config symbol.

## Test Signals

The primary test signal is successful kernel build/link with `CONFIG_OCFS2_FS` enabled. Runtime smoke tests should confirm that the `ocfs2_dlmfs` filesystem type is registered when the resulting module/built-in initializes.
