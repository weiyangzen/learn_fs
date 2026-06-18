<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_yfs.h -->
# sources/distributed-fs/ceph-client/fs/afs/protocol_yfs.h

## Purpose
Defines YFS service IDs, cache-manager and fileserver operation numbers, XDR wire structures, conversion helpers, volume/lock constants, and capability flags.

## Important APIs, Types, And Functions
Key definitions include `YFS_FS_SERVICE`, `YFS_CM_SERVICE`, `enum YFS_CM_Operations`, `enum YFS_FS_Operations`, `struct yfs_xdr_u64`, `xdr_to_u64()`, `u64_to_xdr()`, YFS fid/status/callback/store/volsync/volume-status structs, volume type flags, lock types, and capability masks.

## Control Flow
No runtime flow in the header. YFS client code uses operation constants to marshal requests and XDR structs to parse replies. Rotation and probe paths switch to YFS op implementations when probes identify a YFS service.

## State And Persistence
No local state. It defines wire formats for server state such as fid, status, callback expiration, volume sync times, ACLs, and locks.

## Dependencies And Integration Points
Used by RxRPC call construction, YFS fileserver clients, cache-manager service handling, capability probing, and validation logic that consumes YFS VolSync/callback replies.

## Risks And Edge Cases
Packed struct layout and endian conversion must match wire ABI exactly. Mis-sized fields or wrong opcodes break interoperability. Signed lock constants and 64-bit conversions are particularly sensitive.

## Test Signals
YFS server mount, capability probe upgrade, 64-bit fetch/store, YFS rename/remove variants, lock operations, callback handling, and VolSync validation are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_yfs.h -->
