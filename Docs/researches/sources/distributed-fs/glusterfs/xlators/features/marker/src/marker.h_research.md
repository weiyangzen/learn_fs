# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.h

## Purpose

`marker.h` defines the private data structures, flags, xattr names, and local-frame helper macros used by the marker translator.

## Important APIs, Types, and Functions

Important constants are `MARKER_XATTR_PREFIX`, `XTIME`, `VOLUME_MARK`, `VOLUME_UUID`, and `TIMESTAMP_FILE`. Feature bits are `GF_QUOTA`, `GF_XTIME`, `GF_XTIME_GSYNC_FORCE`, and `GF_INODE_QUOTA`. The local-management macros `MARKER_INIT_LOCAL`, `ALLOCATE_OR_GOTO`, `MARKER_SET_UID_GID`, `MARKER_RESET_UID_GID`, and `MARKER_STACK_UNWIND` standardize frame-local initialization, root credential override for privileged xattr operations, and local unref after unwinding.

`marker_local_t` stores per-call path state, uid/gid, locks, callback stubs, quota contribution data, file offsets and sizes, fd/frame pointers, quota inode/contribution context, xdata, and flags. `marker_inode_ctx_t` links marker inode context to quota context. `marker_conf_t` stores enabled features, key strings, volume UUID, timestamp file, marker xattr name, quota lock owner, lock, and quota version.

## Control Flow

The header has no runtime control flow, but its macros are embedded throughout `marker.c`. `MARKER_STACK_UNWIND` is especially important because it detaches `frame->local`, unwinds the caller, then releases marker local state.

## State and Persistence Behavior

The structs describe in-memory state only. Persistent marker state lives in xattrs and timestamp files managed by `marker.c`, with these fields holding the configured names and temporary values used to write them.

## Dependencies and Integration Points

The header includes `marker-quota.h` and Gluster UUID compatibility support, and it aliases `quota_local_t` to `marker_local_t` so quota helper code can operate on marker locals. It assumes Gluster frame, loc, dict, inode, iatt, lock, fd, and quota types are available through the included marker/quota headers.

## Risks and Edge Cases

Changing `marker_local_t` fields can break quota helpers that rely on the alias. The uid/gid macros intentionally switch request credentials to root for internal xattr operations; missing the reset path risks leaking privileged credentials on a frame. `MARKER_INIT_LOCAL` requires valid frame roots and must be used before fields such as the lock or refcount are consumed.

## Test Signals

Compile tests should catch struct and macro drift. Runtime tests should exercise all macro paths: normal unwind with local release, privileged xattr get/remove during rename, nested `oplocal` release, and local cleanup when errors occur before child winding.
