<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.h -->
# sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.h

## Purpose
Declares a helper that sends several caller-owned buffers through one vectored-write sequence. The source was read completely for this report.

## Important APIs, Types, And Functions
`MultiBufferWriter`, constructor, `addBufferToSend`, `writeTo`, `hasDataToSend`, and internal `iovec` vector are the API/state.

## Control Flow
Header inline flow initializes `buffersCompletelySent_` and checks whether unsent buffers remain.

## State And Persistence Behavior
Owns only iovec descriptors, not the referenced bytes.

## Dependencies And Integration Points
Depends on platform headers for `iovec` and integrates with network output code.

## Risks And Edge Cases
Lifetime of referenced memory is the main contract risk.

## Test Signals
Socket/write tests should pair this with controlled partial-write fakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/multi_buffer_writer.h -->
