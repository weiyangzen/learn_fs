<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_uae.h -->
# sources/distributed-fs/ceph-client/fs/afs/protocol_uae.h

## Purpose
Defines the Universal AFS Error code namespace used by newer AFS/YFS services to return portable errno-like abort values.

## Important APIs, Types, And Functions
Contains a single enum mapping `UAE*` names to the `0x2f6df00` error table, covering common POSIX errno values plus network, quota, stale, medium, and remote I/O errors.

## Control Flow
No executable control flow. `misc.c` translates selected UAE abort codes to Linux errno values, and rotation code recognizes some UAE values directly for volume/full/quota/I/O decisions.

## State And Persistence
No state. The values are wire ABI constants and must remain stable.

## Dependencies And Integration Points
Integrated with fileserver/VL RPC unmarshalling and abort handling. Complements legacy Vice and VL abort constants.

## Risks And Edge Cases
Because this is a protocol ABI list, changing numeric values breaks interoperability. Only some codes are explicitly translated in `afs_abort_to_error()`; unhandled codes fall back to `-EREMOTEIO`.

## Test Signals
Server abort injection with UAE values should produce expected Linux errno for mapped cases and safe fallback for unmapped cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_uae.h -->
