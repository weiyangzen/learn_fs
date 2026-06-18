# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.h

## Research
`SimpleIntMsg.h` declares the reusable one-int message. `struct SimpleIntMsg` embeds `NetMessage` and an `int value`; inline constructors initialize the base with a caller-supplied type and optional value, and `SimpleIntMsg_getValue` returns it. The header enables many concrete messages to be defined as thin wrappers without custom serialization code.

Control flow is limited to inline initialization and access. State is fixed-size and owned by the message object. Dependencies are `NetMessage.h` and the external `SimpleIntMsg_Ops`. Integration points include simple request/response messages where the message type supplies all context and the integer encodes a node type, status code, or result. Risks are semantic ambiguity of the integer payload, lack of range checking, and missing compile-time distinction between enum domains. Test signals are correct concrete `NETMSGTYPE_*` initialization and deserialization of expected integer result values.
