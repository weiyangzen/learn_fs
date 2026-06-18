<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.h

## Purpose

The header declares the fixed-capacity `OutputBuffer` interface for chunkserver output packet buffering and descriptor flushing.

## Important APIs, Types, and Functions

`OutputBuffer::WriteStatus` defines `WRITE_DONE`, `WRITE_AGAIN`, and `WRITE_ERROR`. Public methods include file/memory/vector `copyIntoBuffer()` overloads, `checkCRC()`, `writeOutToAFileDescriptor()`, `bytesInABuffer()`, `data()`, and `clear()`.

## Control Flow

The header only declares behavior. The intended flow is append bytes into the internal buffer, optionally verify a suffix CRC, repeatedly flush to an output descriptor until done/again/error, then clear or reuse.

## State and Persistence Behavior

The buffer owns an in-memory `std::vector<uint8_t>` of fixed capacity plus first/one-after-last unflushed indices. No file descriptors are owned.

## Dependencies and Integration Points

It includes standard byte/container headers and is included by chunkserver connection packet state in `network_worker_thread.h`.

## Risks and Edge Cases

The API exposes raw `data()` for read-only inspection but cursor state is private, so callers must not assume the returned pointer starts at unflushed data after partial writes. All capacity management is caller responsibility. The vector overload calls `mem.data()` even for empty vectors, relying on C++ guarantees and zero-length copy behavior.

## Test Signals

The provided unit test exercises basic memory-to-pipe flow. Stronger tests would cover partial flush cursor behavior, zero-length appends, capacity overflow assertions, and CRC checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.h -->
