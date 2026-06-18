# sources/distributed-fs/beegfs/common/source/common/storage/StatData.h

## Purpose
Defines BeeGFS stat metadata, timestamp mirroring, sparse-file block accounting, and multiple serialization formats for network and disk inode/dentry contexts.

## Important APIs, Types, And Functions
`StatDataFormat`, `MirroredTimestamps`, and `StatData` are the main exports. Constructors initialize fake data, full stat data, or new file data. APIs cover dynamic update, equality, fake/init/set operations, sparse flags, mirrored timestamps, file size/times/mode/uid/gid/nlink/meta-version getters/setters, block accounting, and `serializeFmt()`/`serializeAs()`.

## Control Flow
`serializeFmt()` conditionally writes flags/mode, network `numBlocks` versus disk sparse `chunkBlocksVec`, timestamps, file-size/nlink/meta-version depending on dir-inode format, uid/gid, and trailing mode if flags were not included.

## State, Persistence, And Dependencies
State includes flags, file size, creation/ctime, nlink, settable attributes, metadata version, and `ChunksBlocksVec`. The header explicitly must stay in sync with client-module `StatData.h`, with server-specific disk serialization differences.

## Integration Points
Used by metadata inodes, dentries, network stat responses, mirroring timestamp sync, and storage dynamic attribute aggregation.

## Risks
Format flags are compact and easy to misuse. Network serialization sends estimated/actual block count but not full chunk block vector. Sparse flag correctness depends on prior dynamic updates. Some getters return `int` for `creationTimeSecs` despite the field being `int64_t`.

## Test Signals
Golden serialization for all formats, sparse/non-sparse block count, mirrored timestamp round trip, constructors, hard-link mutations, metadata version, and client compatibility tests.
