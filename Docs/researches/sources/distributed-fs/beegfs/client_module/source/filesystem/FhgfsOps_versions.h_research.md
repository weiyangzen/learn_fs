# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.h

## Purpose
Declares version-dependent VFS operation signatures and fallback helper APIs needed by the BeeGFS client module.

## Important APIs and Types
The header declares `FhgfsOps_permission()` variants, mount/get_sb variants, `FhgfsOps_statfs()`, `FhgfsOps_flush()`, and `FhgfsOps_initInodeOnce()` variants. It also defines inline or external compatibility helpers for `generic_file_llseek_unlocked`, `set_nlink`, `dentry_path_raw`, `ihold`, `file_dentry`, and `file_inode` when kernels lack them.

## Control Flow
Preprocessor branches select the signature visible to the rest of the client. Inline fallbacks directly manipulate old-kernel fields, for example `inode->i_nlink` and `inode->i_count`.

## State and Persistence
No owned runtime state. The fallback helpers mutate standard VFS structures in the same way newer kernel helpers would.

## Dependencies and Integration Points
Includes Linux module, fs, vfs, pagevec, pagemap, and page flag headers. It is included by superblock and many filesystem operation implementations to normalize kernel APIs.

## Risks
Because the header provides inline definitions, macro mismatches can create duplicate symbols or wrong calling conventions. Old-kernel fallbacks bypass newer helper abstractions and require exact semantic parity.

## Test Signals
Compile-only coverage against the supported kernel matrix is the strongest signal. Runtime smoke tests should cover inode link-count changes, file inode/dentry retrieval, and llseek behavior on old kernels.
