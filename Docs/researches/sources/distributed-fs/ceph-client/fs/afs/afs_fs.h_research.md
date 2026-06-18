# sources/distributed-fs/ceph-client/fs/afs/afs_fs.h

## Purpose
`afs_fs.h` defines AFS file service port/service IDs, operation IDs, and file-server abort/error codes.

## Important APIs, types, and functions
It declares `AFS_FS_PORT`, `FS_SERVICE`, `enum AFS_FS_Operations`, and `enum AFS_FS_Errors`. Operations cover fetch/store data/status/ACL, create/remove/rename/link/symlink/mkdir/rmdir, callback relinquish, volume information/status, locks, lookup, inline bulk status, 64-bit data operations, and capabilities.

## Control flow
RPC client code uses these constants when constructing file-server calls and interpreting protocol aborts.

## State and persistence
No runtime state is stored here; constants model wire protocol contract.

## Dependencies and integration points
It integrates with fsclient/yfsclient, server rotation, error translation, and callback/security code that validates service IDs.

## Risks and test signals
Risks are incorrect IDs or error-code signs breaking interoperability. Test signals include wire traces for every operation family, abort-code translation tests, and compatibility with legacy and extended file-server RPCs.
