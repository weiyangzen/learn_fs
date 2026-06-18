# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/Makefile

## Purpose

`fs/ocfs2/dlm/Makefile` defines the build composition for the OCFS2 O2CB distributed lock manager when `CONFIG_OCFS2_FS_O2CB` is enabled.

## Important APIs, Types, and Functions

The file builds `ocfs2_dlm.o` from `dlmdomain.o`, `dlmdebug.o`, `dlmthread.o`, `dlmrecovery.o`, `dlmmaster.o`, `dlmast.o`, `dlmconvert.o`, `dlmlock.o`, and `dlmunlock.o`. There are no runtime APIs in this file, but its object list decides which DLM implementation units are linked.

## Control Flow

Kbuild includes this directory's object only when O2CB support is configured. The combined object contains domain join/leave, debugfs, worker thread, recovery, mastery, AST/BAST, convert, lock, and unlock logic.

## State and Persistence Behavior

No runtime state is stored here. The file controls compilation and linking only.

## Dependencies and Integration Points

It depends on the `CONFIG_OCFS2_FS_O2CB` Kconfig option and Kbuild's composite-object rules. The resulting `ocfs2_dlm.o` links with OCFS2 filesystem code and the cluster transport.

## Risks and Edge Cases

Removing or misordering an object can cause unresolved symbols or remove a message handler implementation that another DLM unit declares in `dlmcommon.h`. Because DLM files are tightly coupled through shared internal prototypes, configuration matrix builds are the main guard.

## Test Signals

Build with `CONFIG_OCFS2_FS_O2CB=y` and as module if supported, and build with it disabled. Runtime signals include DLM domain registration, lock/unlock/convert paths, recovery, and debugfs availability.
