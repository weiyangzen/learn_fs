<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/output_buffer_unittest.cc

## Purpose

This GoogleTest file validates the simplest `OutputBuffer` write path: append bytes from memory, flush them to a pipe, read them back, and compare byte values.

## Important APIs, Types, and Functions

It defines `TEST(OutputBufferTests, outputBuffersTest)`. The test uses `pipe2(..., O_NONBLOCK)` when available, optional `F_SETPIPE_SZ`, `OutputBuffer::copyIntoBuffer()`, `writeOutToAFileDescriptor()`, and `read()`.

## Control Flow

The test creates a 512 KiB buffer and pipe, fills a 10-byte memory buffer with value 17, appends it, then loops flushing until `WRITE_DONE`, sleeping if the nonblocking pipe returns `WRITE_AGAIN`. It reads the pipe and asserts all bytes match.

## State and Persistence Behavior

State is limited to the test pipe descriptors and stack buffer. It closes both pipe ends at the end of the test.

## Dependencies and Integration Points

It depends on GoogleTest, POSIX pipe/fcntl/read/close APIs, and the `OutputBuffer` public interface.

## Risks and Edge Cases

Coverage is narrow: it does not force partial writes, `WRITE_ERROR`, file-copy input, CRC checking, `clear()`, or buffer exhaustion. On systems without `pipe2`, the pipe may be blocking despite the test's nonblocking intent.

## Test Signals

Passing this test signals basic memory append and descriptor write correctness. It is not sufficient to validate nonblocking network behavior under backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/output_buffer_unittest.cc -->
