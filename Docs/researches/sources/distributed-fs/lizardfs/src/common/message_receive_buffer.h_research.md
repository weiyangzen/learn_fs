<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.h -->
# sources/distributed-fs/lizardfs/src/common/message_receive_buffer.h

## Purpose
Declares a helper for accumulating framed LizardFS packets from sockets. The source was read completely for this report.

## Important APIs, Types, And Functions
`readFrom`, `removeMessage`, `hasMessageHeader`, `hasMessageData`, `isMessageTooBig`, `getMessageHeader`, and `getMessageData` define the API.

## Control Flow
Inline checks parse the packet header once enough bytes are present and compare received bytes to header length.

## State And Persistence Behavior
Owns a fixed-capacity byte vector and count of received bytes.

## Dependencies And Integration Points
Depends on `datapack.h`, `massert.h`, and `protocol/packet.h`.

## Risks And Edge Cases
Returned data pointer is valid only until the next read/remove. Header length is trusted for size checks and can represent malicious large payloads.

## Test Signals
Protocol-buffer unit tests and fuzzing of malformed headers would be useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/message_receive_buffer.h -->
