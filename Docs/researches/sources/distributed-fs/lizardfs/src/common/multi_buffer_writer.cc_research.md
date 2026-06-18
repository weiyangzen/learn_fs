<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.cc -->
# sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.cc

## Purpose
Implements vectored writes over multiple buffers, with a Windows compatibility `writev` implementation. The source was read completely for this report.

## Important APIs, Types, And Functions
`MultiBufferWriter::addBufferToSend` and `writeTo` are implemented; Windows builds also define `writev` using socket send/poll wrappers.

## Control Flow
Buffers are appended as `iovec`s. `writeTo` calls `writev` starting at the first unsent buffer, then advances `buffersCompletelySent_` and adjusts the first partial iovec after short writes.

## State And Persistence Behavior
Runtime state is the vector of iovecs and count of fully sent buffers. It references caller-owned memory; no persistence.

## Dependencies And Integration Points
Depends on sockets wrappers on Windows and POSIX `writev` elsewhere. Used by packet send paths needing scatter/gather writes.

## Risks And Edge Cases
Caller must keep buffer memory alive and immutable until fully sent. `writeTo` assumes it is not called after all buffers are sent unless underlying `writev` tolerates zero count.

## Test Signals
Needs tests for full write, partial write, EAGAIN/error, empty/all-sent behavior, and Windows compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.cc -->
