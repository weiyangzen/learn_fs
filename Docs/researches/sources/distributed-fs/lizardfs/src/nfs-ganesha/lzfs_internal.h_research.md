# sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.h

## Purpose
Defines private FSAL module/export/handle/FD/state/pNFS structures, constants, and shared function declarations for the LizardFS NFS-Ganesha plugin.

## Important APIs, Types, And Functions
Defines `lzfs_fsal_module`, `lzfs_fsal_export`, `lzfs_fsal_fd`, `lzfs_fsal_state_fd`, `lzfs_fsal_key`, `lzfs_fsal_handle`, `lzfs_fsal_ds_wire`, and `lzfs_fsal_ds_handle`. Constants include lease time, supported attribute mask, largest pNFS stripe count, standard chunk part type, backup DS count, and TCP protocol number. Declares shared functions from internal, export, handle, pNFS, DS, and ACL modules.

## Control Flow
This header is included by all FSAL implementation files to share container layouts and operation initialization hooks.

## State And Persistence Behavior
Defines all in-process state carriers for exports, object handles, open file descriptors, stateful opens, and pNFS DS handles. Remote persistence is outside the header.

## Dependencies And Integration Points
Depends on Ganesha `fsal_api.h`/commonlib, fileinfo cache, and LizardFS C API. It is the internal ABI of the plugin.

## Risks And Edge Cases
Because structs are shared across C files, layout changes have broad impact. `kDisconnectedChunkserverVersion` macro includes a trailing semicolon, which is harmless in assignments/comparisons as used but fragile. `LZFS_SUPPORTED_ATTRS` advertises ACL and rich attribute support that must remain consistent with implementations.

## Test Signals
Compilation across all FSAL modules is the first signal; runtime tests should validate advertised capabilities against actual operation support.
