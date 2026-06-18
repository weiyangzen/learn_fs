<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_afs.h -->
# sources/distributed-fs/ceph-client/fs/afs/protocol_afs.h

## Purpose
Defines small AFS3 fileserver capability constants shared by protocol clients.

## Important APIs, Types, And Functions
Defines `AFSCAPABILITIESMAX` and capability bits for UAE error translation, 64-bit file operations, write-lock ACL behavior, and historical sane ACL signaling.

## Control Flow
No executable control flow. Capability replies parsed elsewhere use these masks to set server feature flags such as 64-bit fetch/store support and error translation behavior.

## State And Persistence
No state. The constants influence runtime server capability state stored in `struct afs_server`.

## Dependencies And Integration Points
Used by fileserver capability probing/client code together with AFS3/YFS operation selection and error translation.

## Risks And Edge Cases
Wrong bit assignments would mis-detect server abilities, causing unsupported opcodes or missed 64-bit operation support. Deprecated capability meanings should not be overinterpreted.

## Test Signals
Probe OpenAFS/AFS3 servers with different capabilities and verify selected RPC variants and error mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_afs.h -->
