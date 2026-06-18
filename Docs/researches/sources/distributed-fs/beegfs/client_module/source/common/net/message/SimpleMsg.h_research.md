# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.h

## Research
`SimpleMsg.h` declares the minimal header-only message wrapper. `struct SimpleMsg` embeds `NetMessage`, and `SimpleMsg_init` initializes it with a caller-specified message type and `SimpleMsg_Ops`. It is used when all semantics come from the message type and common header fields.

Control flow is only inline initialization; serialization/deserialization behavior is in the `.c` file. State is fixed-size and has no owned payload resources. Dependencies are `NetMessage.h`. Integration points include request wrappers that do not require payload data, and receive-side messages that override `ops` after initializing as a simple message. Risks are missing an ops override for messages with custom `processIncoming`, and future protocol changes adding payload without updating derived wrappers. Test signals are message length checks and successful server handling of header-only requests.
