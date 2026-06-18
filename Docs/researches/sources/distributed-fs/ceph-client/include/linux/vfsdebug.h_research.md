# sources/distributed-fs/ceph-client/include/linux/vfsdebug.h

## Purpose
This header provides VFS-specific BUG/WARN wrappers that optionally dump inode context before triggering debug assertions.

## Important APIs, types, and functions
With `CONFIG_DEBUG_VFS`, it exports `dump_inode()` and macros `VFS_BUG_ON`, `VFS_WARN_ON`, `VFS_WARN_ON_ONCE`, `VFS_WARN_ONCE`, `VFS_WARN`, `VFS_BUG_ON_INODE`, and `VFS_WARN_ON_INODE`. Disabled builds use `BUILD_BUG_ON_INVALID()` to type-check conditions without runtime checks.

## Control flow, state, and persistence
Debug builds evaluate conditions at runtime; inode-specific forms call `dump_inode()` before BUG/WARN. Non-debug builds compile away runtime checks while preserving expression validation. There is no persistent state.

## Dependencies and integration points
It depends on bug/warn infrastructure and inode declarations. It integrates with VFS and filesystem invariant checks.

## Risks and test signals
Risks include side effects in conditions disappearing in non-debug builds and crashing debug kernels via BUG_ON. Tests should compile both configs, trigger warning paths with fake inodes, and verify no side-effect reliance.
