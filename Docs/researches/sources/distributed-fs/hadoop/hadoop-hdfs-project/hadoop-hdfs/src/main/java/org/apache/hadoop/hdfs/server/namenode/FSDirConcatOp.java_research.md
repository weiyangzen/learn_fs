# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirConcatOp.java

## Purpose
`FSDirConcatOp` implements HDFS file concat: append the blocks of multiple source files to a target file and remove the sources from the namespace. It enforces the concat contract that sources and target live in the same directory and are compatible in snapshots, construction state, block size, encryption, and erasure coding.

## Important APIs, Types, And Functions
- `concat` is the checked entry point and returns audit `FileStatus`.
- `validatePath`, `verifyTargetFile`, `verifySrcFiles`, `computeQuotaDeltas`, and `verifyQuota` implement preconditions.
- `unprotectedConcat` performs the locked namespace/block mutation.
- Key types are `INodeFile`, `INodeDirectory`, `INodesInPath`, `QuotaCounts`, `BlockStoragePolicy`, `StorageType`, and `FSDirEncryptionZoneOp`.

## Control Flow
The entry point rejects reserved concat paths, resolves the target, checks write permission on the target, verifies the target is a closed file outside an encryption zone, validates each source with read permission and parent write permission, rejects duplicate sources, sources in snapshots or multi-reference snapshot state, under-construction/empty sources, larger preferred block sizes, and EC policy mismatch. It then takes the directory write lock and calls `unprotectedConcat`. That routine computes namespace/storage quota deltas, records target modification for snapshots, concatenates source blocks into the target, clears and removes source files from their parent and inode map, updates target and parent modification time, and applies quota deltas.

## State And Persistence Behavior
The operation persists through `logConcat(target, srcs, timestamp, logRetryCache)` after in-memory mutation. Source inodes are removed, source blocks are transferred/cleared, target block list and mtime change, parent mtime changes, namespace quota drops by source count, and storage/type quota may change if source replication differs from target replication.

## Dependencies And Integration Points
It depends on `FSDirectory` for path resolution, quota verification, inode-map removal, and locks; `INodeFile.concatBlocks` and `BlockManager` for block ownership; `FSDirEncryptionZoneOp` to disallow encrypted concat; snapshot reference classes to reject unsafe sources; and edit-log replay via `unprotectedConcat`.

## Risks And Edge Cases
Quota accounting must reflect replication and storage type transitions, not only namespace removal. Snapshot references are especially sensitive because source files are deleted while their blocks move. Encryption zones are disallowed entirely, and EC policy mismatches are rejected to avoid mixed block layouts in one file.

## Test Signals
Tests should cover duplicate sources, target equal to source, cross-directory rejection, under-construction/empty sources, snapshot-held sources, encryption-zone target rejection, EC policy mismatch, quota delta behavior when replication differs, edit-log replay, and successful concat preserving block order while removing source inodes.
