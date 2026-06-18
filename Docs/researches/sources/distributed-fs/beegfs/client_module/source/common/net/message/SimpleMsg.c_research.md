# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.c

## Research
`SimpleMsg.c` implements payload ops for header-only messages. `SimpleMsg_serializePayload` intentionally emits nothing, while `SimpleMsg_deserializePayload` always returns true because the message type and common header carry all information. The ops table delegates incoming processing and feature flags to `NetMessage` defaults unless a derived wrapper overrides the ops pointer.

Control flow is no-op payload handling. State is only the inherited `NetMessage` header. Dependencies are `SimpleMsg.h` and base message functions. Integration points include heartbeat requests, target mapping requests, and other protocol requests where the `NETMSGTYPE_*` alone identifies the action. Risks are accidentally choosing `SimpleMsg` for a wire type that later gained payload fields, and accepting extra payload bytes because no message-specific content is consumed. Test signals are header-only message length equal to `NETMSG_HEADER_LENGTH` and dispatch paths that override processing where needed.
