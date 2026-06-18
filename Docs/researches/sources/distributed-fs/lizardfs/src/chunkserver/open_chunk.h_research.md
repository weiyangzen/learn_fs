<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/open_chunk.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/open_chunk.h

## Purpose

`OpenChunk` is an RAII wrapper for a chunkserver `Chunk` that has been found/locked and may have an open file descriptor and optional MooseFS CRC data buffer. It centralizes cleanup of descriptors, error reporting, and `hdd_chunk_release()`.

## Important APIs, Types, and Functions

The class has default, `Chunk*`, and move constructors, move assignment, destructor, `canRemove()`, `purge()`, and `crc_data()`. It stores `Chunk *chunk_`, fallback descriptor `fd_`, and `std::unique_ptr<MooseFSChunk::CrcDataContainer> crc_`.

## Control Flow

Construction captures the chunk pointer and current descriptor and allocates CRC storage for MooseFS-format chunks. Destruction closes `chunk_->fd` when present, reports close failures as damaged chunks, resets the chunk descriptor to `-1`, and releases the locked chunk. If `purge()` was called, the wrapper forgets the chunk, keeps the descriptor, and closes only that descriptor later.

## State and Persistence Behavior

The class does not persist metadata itself, but it mutates persistent chunk state indirectly through close-error reporting and damage reporting. Its correctness depends on the caller already holding the chunk lock.

## Dependencies and Integration Points

It depends on `chunkserver/chunk.h`, `hddspacemgr.h`, `hdd_chunk_trylock()`, `hdd_chunk_release()`, `hdd_error_occured()`, and `hdd_report_damaged_chunk()`.

## Risks and Edge Cases

Move assignment overwrites any existing owned chunk/fd without first releasing it, so callers should only move into empty/discarded wrappers. `crc_data()` asserts that CRC storage exists and is only valid for MooseFS chunks. `purge()` requires `chunk_` and changes ownership semantics; misuse can leak locks or close the wrong descriptor.

## Test Signals

Expected coverage is chunkserver HDD tests that close chunks on success/error, remove locked chunks, purge inaccessible chunks, and read MooseFS CRC data. No direct unit test is included in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/open_chunk.h -->
