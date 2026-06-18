# sources/distributed-fs/orangefs/src/client/usrint/iocommon.h

## Purpose
`iocommon.h` declares the shared low-level PVFS/OrangeFS user-interface routines implemented in `iocommon.c`. It is the contract between POSIX-facing wrappers, async/cache code, descriptor utilities, and the PVFS system-interface layer.

## Important APIs, Types, And Macros
The cache helper structs `ucache_req_s` and `ucache_copy_s` describe cache block tags, shared-memory block pointers/indexes, and cache-to-user-buffer copy operations. The global `pvfs_errno` reports PVFS-specific errors when `errno` is set to `EIO`. The prototypes cover initialization, credentials, path expansion and lookup, server-list parsing, file creation/open/truncate/lseek/remove/rename, blocking and nonblocking I/O, attribute/stat/statfs operations, extended attributes, ownership/mode changes, directory creation, readlink/symlink, directory reads, access checks, and sendfile.

The `IOCOMMON_RETURN_ERR` macro jumps to `errorout` when a conventional `-1` return is seen. `IOCOMMON_CHECK_ERR` is the key PVFS error adapter: it restores `errno` to `orig_errno`, maps PVFS non-errno errors into `pvfs_errno` plus `EIO`, maps ordinary PVFS errors through `PINT_errno_mapping`, converts the return to `-1`, and jumps to `errorout`.

## Control Flow Contract
Functions using this header generally follow a common pattern: define `int rc`, `int orig_errno = errno`, perform PVFS work, use the macros after PVFS calls, and have an `errorout:` cleanup label returning `rc` or an API-specific value. Callers are expected to pass valid `pvfs_descriptor` objects for descriptor-based operations and `PVFS_object_ref` values for direct object operations.

## State And Persistence Behavior
The header exposes the stateful nature of the subsystem through descriptors, credentials, cache block descriptions, directory tokens hidden inside descriptors, and `pvfs_errno`. Persistent server-side changes are mediated by the declared mutation APIs, while local cache state is coordinated through cache helper structs and `ucache` functions.

## Dependencies And Integration Points
The header includes PVFS public types (`pvfs2.h`, `pvfs2-types.h`, `pvfs2-request.h`, `pvfs2-debug.h`) and `pvfs-path.h`. It assumes POSIX types such as `mode_t`, `off64_t`, `struct iovec`, `struct stat`, `struct statfs`, `struct dirent`, and descriptor types from usrint headers are visible through include order. `posix-pvfs.c`, `aiocommon.c`, `ucache.c`, and path utilities consume this interface.

## Risks
The macros require local variables named `orig_errno`, `rc`, and an `errorout` label; using them outside that pattern is unsafe. `IOCOMMON_CHECK_ERR` mutates `errno` even on errors from PVFS calls, so callers must not rely on syscall-side errno after PVFS returns. Cache helper structs are compiled only meaningfully with `PVFS_UCACHE_ENABLE`, but their declarations are always present. The declared `iocommon_ensure_init` is not implemented in the inspected `iocommon.c`, so link coverage should confirm whether another file provides it or whether it is stale.

## Test Signals
Compile tests should include all consumers of `iocommon.h` and verify prototypes match implementations. Unit or integration tests should intentionally trigger PVFS errors that map to ordinary errno and non-errno PVFS errors, verifying `pvfs_errno` behavior. API tests should cover each descriptor/object operation through the POSIX wrapper layer to ensure the declared contract remains synchronized with implementation.
