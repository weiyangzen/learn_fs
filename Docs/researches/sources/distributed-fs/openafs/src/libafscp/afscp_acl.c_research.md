<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_acl.c -->
# sources/distributed-fs/openafs/src/libafscp/afscp_acl.c

## Purpose
Implements libafscp ACL fetch and store wrappers for AFS directories. It locates the volume and file servers for a directory FID, tries each server address, calls the RXAFS ACL RPC, updates local stat cache on success, and invalidates stat cache plus sets `afscp_errno` on failure.

## Important APIs, Types, And Functions
The exported functions are `afscp_FetchACL` and `afscp_StoreACL`. Important dependencies are `afscp_VolumeById`, `afscp_ServerByIndex`, `RXAFS_FetchACL`, `RXAFS_StoreACL`, `RXAFS_OldStoreACL`, `_StatStuff`, `_StatInvalidate`, `AFSOpaque`, `AFSFetchStatus`, `AFSVolSync`, and `AFSFid`.

## Control Flow
Both functions resolve the volume from the FID's cell and volume id, then iterate volume server indexes and each server address. Fetch calls `RXAFS_FetchACL`, validates returned ACL data as a NUL-terminated non-empty string, and breaks on the first nonnegative RPC result. Store calls `RXAFS_StoreACL`, falling back to `RXAFS_OldStoreACL` on `RXGEN_OPCODE`. Success updates cached status; failure invalidates the stat cache and returns `-1`.

## State And Persistence
The functions mutate the caller-provided ACL buffer for fetch, remote ACL state for store, local stat cache entries through `_StatStuff` or `_StatInvalidate`, and global `afscp_errno`. They do not allocate persistent local state.

## Dependencies And Integration Points
This file integrates libafscp FID/volume/server lookup with fileserver ACL RPCs and the local stat-cache implementation from `afscp_internal.h`. It is archived into `libafscp.a`.

## Risks And Test Signals
Risks include interpreting negative/nonnegative RPC status incorrectly, partial ACL buffers from failed fetches, malformed ACL validation edge cases, fallback compatibility with old fileservers, and trying stale server connections before valid ones. Useful tests include fetch/store against modern and old fileservers, malformed ACL response handling, multi-address retry, missing volume errors, and stat-cache invalidation/update verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_acl.c -->
