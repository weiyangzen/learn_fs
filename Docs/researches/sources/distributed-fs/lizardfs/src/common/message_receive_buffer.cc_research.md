<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.cc -->
# sources/distributed-fs/lizardfs/src/common/message_receive_buffer.cc

## Purpose
Implements socket reads into a fixed-size message buffer and removal of consumed LizardFS packets. The source was read completely for this report.

## Important APIs, Types, And Functions
`MessageReceiveBuffer::readFrom` and `removeMessage` are implemented.

## Control Flow
`readFrom` receives available bytes after the current fill position through `tcprecv` and updates `bytesReceived_`. `removeMessage` computes header plus payload size, memmoves any extra bytes down, and reduces the received count.

## State And Persistence Behavior
Runtime state is the vector buffer and received byte count. No persistence.

## Dependencies And Integration Points
Depends on packet header serialization and socket wrappers. Used by connection handlers reading framed protocol messages.

## Risks And Edge Cases
Callers must check `isMessageTooBig` before the buffer fills, otherwise `readFrom` asserts when full. `removeMessage` assumes a full message is present.

## Test Signals
Needs tests for partial header, full body, multiple messages in buffer, oversized messages, and socket error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.cc -->
