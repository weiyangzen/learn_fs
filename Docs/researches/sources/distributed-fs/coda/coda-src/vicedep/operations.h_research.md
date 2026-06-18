# sources/distributed-fs/coda/coda-src/vicedep/operations.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/operations.h` is the shared declaration header for file-server operation validation, semantic checks, data-transfer helpers, metadata mutation helpers, quota updates, and object release/commit coordination.

## Important APIs, Types, and Functions

It defines `typedef int (*VCP)(int, VnodeType, void *, void *)` for version comparison callbacks. It declares `ValidateParms`, `AllocVnode`, all `Check*Semantics` routines, `PerformFetch`, `FetchBulkTransfer`, `PerformGetAttr`, `PerformGetACL`, `PerformStore`, `StoreBulkTransfer`, `PerformSetAttr`, `PerformSetACL`, `PerformCreate`, `PerformRemove`, `PerformLink`, `PerformRename`, `PerformMkdir`, `PerformRmdir`, `PerformSymlink`, `PerformSetQuota`, `PutObjects`, and `SpoolRenameLogRecord`.

## Control Flow

The header mirrors the server operation pipeline: parameter validation, object allocation/locking, semantic checks, transfer or mutation, and final release. Callers in RPC stubs and resolution/reintegration code compose these functions according to the operation being executed.

## State and Persistence Behavior

The header itself has no state. Its declared functions mutate vnode/volume/directory/inode state, adjust quotas, schedule replicated COP state, and commit/abort changes through `PutObjects`.

## Dependencies and Integration Points

It depends on server types such as `RPC2_Handle`, `ClientEntry`, `Volume`, `Vnode`, `ViceFid`, `ViceVersionVector`, `Rights`, `AL_AccessList`, `dlist`, `vle`, `DirInode`, and transaction annotations. It is included by `srvproc.cc`, `srvproc2.cc`, generated server code, and conflict-resolution modules that need to reuse normal server semantics.

## Risks and Edge Cases

The prototypes encode many raw pointers, optional defaults, and output parameters; argument-order drift between declarations and definitions would be severe. The `VCP` callback receives untyped `void *` version arguments, so callers must pass the correct object for replicated vs non-replicated operations. Some defaults suppress protection checks or target-nonempty checks, which is powerful for repair/resolution but risky if exposed accidentally.

## Test Signals

Compile with strict prototype checking; exercise each declared check/perform pair through both client RPCs and resolution code; add ABI-style tests for expected error returns when version comparison, protection, type, or directory integrity checks fail.
