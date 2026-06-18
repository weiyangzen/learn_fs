# sources/distributed-fs/lizardfs/src/protocol/cltoma_unittest.cc

## Purpose
Validates selected client-to-master packet serialization wrappers.

## Important APIs, Types, And Functions
Tests `fuseReadChunk`, `fuseWriteChunk`, `fuseWriteChunkEnd`, `chunksHealth`, `fuseDeleteAcl`, `fuseGetAcl`, and `fuseSetAcl`. Uses in/out pair helpers, packet header helpers, and an `AccessControlList` sample.

## Control Flow
Each test serializes fields, verifies the command id, strips the header, deserializes, and compares outputs. ACL set additionally builds a POSIX ACL with mode and named group entry and compares full ACL equality.

## State And Persistence Behavior
No persistent state. Tests validate byte-vector serialization only.

## Dependencies And Integration Points
Depends on `protocol/cltoma.h`, GoogleTest, and unittest helpers. Protects master communication used by mount/client and administrative paths.

## Risks And Edge Cases
The test file covers a small fraction of `cltoma.h`. It does not test quotas, locks, admin commands, paged directory/trash/reserved listings, task/snapshot packets, rich ACLs, legacy ACLs, malformed buffers, or version mismatch handling.

## Test Signals
Passing tests provide confidence for chunk allocation/finish packet formats and basic ACL packet formats.
