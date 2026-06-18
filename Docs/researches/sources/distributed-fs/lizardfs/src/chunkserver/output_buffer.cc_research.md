<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.cc

## Purpose

This file implements `OutputBuffer`, a fixed-capacity byte buffer used to accumulate packet/file data and flush it to a nonblocking descriptor.

## Important APIs, Types, and Functions

Implemented methods are the constructor/destructor, `writeOutToAFileDescriptor()`, `bytesInABuffer()`, `clear()`, `copyIntoBuffer(int,size_t,off_t*)`, `copyIntoBuffer(const void*,size_t)`, and `checkCRC()`.

## Control Flow

The constructor allocates `internalBufferCapacity` bytes and initializes unflushed cursors. Memory copies append directly to the unflushed tail. File copies loop with `pread()` until the requested length is read or a nonpositive result occurs. Flush loops with `write()` until all buffered bytes are written, returns `WRITE_AGAIN` on `EAGAIN` or zero writes, and `WRITE_ERROR` for other failures.

## State and Persistence Behavior

State is the internal vector and two cursor indices. It does not own input or output descriptors and does not advance the optional `offset` pointer passed to `copyIntoBuffer`, so callers must manage file position semantics themselves.

## Dependencies and Integration Points

It depends on POSIX `pread`/`write`, `common/crc.h` for `mycrc32`, and assertion helpers. Chunkserver network code stores `OutputBuffer` instances inside outgoing packet records.

## Risks and Edge Cases

Capacity violations abort through `eassert`. `copyIntoBuffer(int, ..., offset)` repeatedly passes the same offset value and does not increment `*offset`, which is only correct if callers intend fixed-offset reads or pass null for implicit offset zero behavior; otherwise it can duplicate data. `checkCRC()` uses an assertion that rejects checking from index zero, so boundary cases are debug-sensitive.

## Test Signals

`output_buffer_unittest.cc` covers memory append and pipe flush. More signals should include short writes, `EAGAIN`, file reads with offsets, CRC success/failure, and buffer boundary assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer.cc -->
