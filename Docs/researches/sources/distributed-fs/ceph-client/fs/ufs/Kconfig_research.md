# sources/distributed-fs/ceph-client/fs/ufs/Kconfig

## Purpose
`Kconfig` exposes Linux UFS filesystem build options: core UFS support, experimental write support, and debug logging.

## Important APIs, types, and functions
It defines `CONFIG_UFS_FS` as a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`, `CONFIG_UFS_FS_WRITE` as a dangerous write-support boolean depending on UFS, and `CONFIG_UFS_DEBUG` as a debug-message boolean.

## Control flow
The file participates in kernel configuration rather than runtime code. Selecting UFS builds the module or builtin object; write support enables mutation paths elsewhere in the filesystem; debug support feeds the Makefile's `-DDEBUG`.

## State and persistence
No runtime state exists. The choices determine whether UFS code can be loaded and whether write paths that mutate inode, directory, cylinder group, and bitmap metadata are compiled or reachable.

## Dependencies and integration points
It integrates with kbuild, `fs/ufs/Makefile`, buffer-head infrastructure, and admin documentation for UFS mount behavior.

## Risks and test signals
Risks are user misunderstanding of read-only versus write-capable UFS, especially because UFS2 is documented as read-only supported while write support is marked dangerous. Test signals include build coverage for `n`, `m`, and `y`, builds with write support disabled/enabled, and debug builds verifying `UFSD` logging compiles.
