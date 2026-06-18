# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.c

## Purpose
Provides Linux-kernel-version compatibility implementations for permission, statfs, mount entry points, file flush, inode-cache construction, and older kernel helper emulation.

## Important APIs and Functions
`FhgfsOps_permission()` disables RCU path walking where necessary and delegates permission checks to the appropriate generic permission API. `FhgfsOps_statfs()` fills `kstatfs` from `StatFsCache`. `FhgfsOps_getSB()`/`FhgfsOps_mount()` adapt to old/new mount APIs. `FhgfsOps_flush()` invokes BeeGFS close-time flushing. `FhgfsOps_initInodeOnce()` initializes cached BeeGFS inode objects. Older kernels may get emulated `generic_file_llseek_unlocked()`.

## Control Flow
Permission checks return `-ECHILD` for RCU walk flags so VFS retries in ref-walk mode, then use idmapped/userns/generic permission paths. Statfs initializes fields, queries cached total/free space, converts BeeGFS error codes to Linux errors, and rounds byte totals into `BEEGFS_STATFS_BLOCKSIZE` units. Flush logs the operation and calls `__FhgfsOps_flush()` with asynchronous cleanup allowances.

## State and Persistence
This file does not own durable state. It reads `App`, `Config`, `StatFsCache`, file/dentry/inode state, and initializes slab-created inode objects. Statfs reports cached distributed storage values rather than local disk values.

## Dependencies and Integration Points
Integrates with `FhgfsOpsSuper`, inode/file/dir helpers, remoting, `NoAllocBufferStore`, `StatFsCache`, and `OsCompat`. It is a compatibility layer for many `KERNEL_HAS_*` feature macros.

## Risks
Cross-version signatures are fragile; incorrect macro detection can produce ABI mismatches. Statfs depends on cache freshness and can return remote I/O errors. Flush errors do not imply data is permanently lost because flusher references may remain, but caller-visible close behavior depends on `__FhgfsOps_flush()` semantics.

## Test Signals
Build matrix across supported kernels, permission RCU-walk regression tests, statfs cache success/failure, close/flush with delayed writeback, and slab constructor tests for inode initialization.
