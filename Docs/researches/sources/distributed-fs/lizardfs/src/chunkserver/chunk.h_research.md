# sources/distributed-fs/lizardfs/src/chunkserver/chunk.h

## Purpose
`chunk.h` declares chunkserver disk chunk types, folder/disk state structures, and the `Chunk` class hierarchy used by storage, scanning, replication, and I/O code.

## Important APIs, Types, And Functions
- Constants: `STATSHISTORY`, `LASTERRSIZE`, and `kHddBlockSize`.
- `ChunkState` enumerates availability/deletion lifecycle states: available, locked, deleted, and to-be-deleted.
- `cntcond` and `ioerror` are support structures for waiters and recent disk errors.
- `folder` stores path, scan/migration states, capacity, statistics history, last errors, chunk counts, device/lock data, scan/migration threads, test chunk lists, and linked-list linkage.
- `Chunk` declares naming, rename, layout, block offset/size validation, chunk format, subfolder helpers, and shared fields.
- `MooseFSChunk` declares header/CRC/signature behavior for `.mfs`.
- `InterleavedChunk` declares `.liz` interleaved block behavior.
- `IF_MOOSEFS_CHUNK` and `IF_INTERLEAVED_CHUNK` are dynamic-cast convenience macros.

## Control Flow
Storage code creates a concrete `Chunk` subtype based on parsed chunk format or desired output format. It uses virtual methods to translate block numbers to file offsets and validate persisted file sizes. Folder scan/migration code updates `folder` scan and migration bitfields and links chunks through the public intrusive pointers.

## State And Persistence
This header defines much of the chunkserver's in-memory representation of persisted storage: folder paths/capacity/statistics and chunk ids, versions, fds, block counts, owners, layout, deletion flags, and scan/test links. Persistent chunk files are named and interpreted through the `Chunk` methods declared here.

## Dependencies And Integration Points
It integrates with `chunk_format.h`, `ChunkPartType`, `DiskInfo`, `MFSCommunication` constants, condition variables, threads, and POSIX device/inode types. Many chunkserver modules include this header through HDD manager, parser, creator, and tests.

## Risks
- Public mutable fields make invariants spread across modules rather than enforced by methods.
- Bitfield state constants for scans/migration/removal must remain consistent with all scanner code.
- `setBlockCountFromFizeSize` contains a misspelling in the API name, which is harmless but sticky ABI/source surface.
- The folder struct combines persistence, statistics, scanning, migration, and locking concerns, increasing accidental coupling.

## Test Signals
`chunk_unittest.cc` directly covers some virtual behavior and naming. Broader folder state and scan/migration fields are not covered in listed tests.
