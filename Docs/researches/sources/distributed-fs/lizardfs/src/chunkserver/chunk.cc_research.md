# sources/distributed-fs/lizardfs/src/chunkserver/chunk.cc

## Purpose
`chunk.cc` implements chunk metadata and disk layout behavior for MooseFS-compatible and LizardFS interleaved chunk formats, including filenames, subfolder placement, block offsets, file-size validation, and header sizing.

## Important APIs, Types, And Functions
- `Chunk::Chunk` initializes common runtime metadata: owner folder, fd, version, block count, state, refcount, layout, deletion flags, and read-ahead expectation.
- `Chunk::generateFilenameForVersion` builds disk paths from owner path, subfolder, chunk type prefix, chunk id/version, and extension.
- `Chunk::renameChunkFile` renames the on-disk file and updates version/layout on success.
- `Chunk::maxBlocksInFile` maps standard/XOR/EC data part counts to per-slice block counts.
- `Chunk::getSubfolderNumber`, `getSubfolderNameGivenNumber`, and `getSubfolderNameGivenChunkId` implement current and older directory layouts.
- `MooseFSChunk` implements header-aware offsets, header size, CRC/signature offsets, header readahead, and MooseFS file-size validation.
- `InterleavedChunk` implements block records of data plus CRC with `.liz` file format semantics.

## Control Flow
File naming starts with `owner->path`, then a layout-specific subdirectory (`chunksXX` for current layout), then `chunk_` plus optional XOR or EC prefix. Standard chunks have no prefix. MooseFS format keeps `.mfs`; interleaved format replaces the extension with `.liz`. Rename first computes old/new names, calls POSIX `rename`, then updates in-memory layout and version only after success.

MooseFS chunks place a signature block and CRC array before data. Standard chunks use the exact required signature-plus-CRC size; XOR/EC chunks round the header up to a 4 KiB disk block. Interleaved chunks store each block as `MFSBLOCKSIZE` data plus a 4-byte CRC, so offsets and file sizes are simple multiples of `kHddBlockSize`.

## State And Persistence
The `Chunk` object mirrors persisted chunk files. Persistent effects occur through filename generation and `renameChunkFile`. Header/layout methods determine how other storage code reads and writes chunk contents. In-memory state includes owner folder, fd, chunk id/version, block count, type, layout version, flags, and linked-list fields for scans/tests.

## Dependencies And Integration Points
The file depends on `folder` from `chunk.h`, `ChunkPartType`, `slice_traits`, `ChunkFormat`, POSIX `rename`, `posix_fadvise` or macOS `F_RDADVISE`, and protocol constants such as `MFSBLOCKSIZE` and `MFSBLOCKSINCHUNK`. It is used by HDD space manager, filename parser/signature code, tests, and replication file creation.

## Risks
- `generateFilenameForVersion` assumes `owner` and `owner->path` are valid.
- Filename generation and parser rules must remain in lockstep across standard, XOR, EC, `.mfs`, and `.liz` formats.
- `sprintf` writes into fixed buffers, currently sized for known hexadecimal strings; future format expansion would need care.
- Header size math is format-critical; changing `ChunkPartType` or block-count rules can break compatibility with existing chunks.

## Test Signals
`chunk_unittest.cc` covers `maxBlocksInFile`, generated filenames for standard and XOR chunks, and current subfolder naming. It does not cover EC filenames, old directory layout names, `renameChunkFile`, or file-size validation edge cases.
