# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatRequestMsgEx.h

## Research
`HeartbeatRequestMsgEx.h` declares a header-only heartbeat request that overrides processing. It embeds `SimpleMsg`, initializes as `NETMSGTYPE_HeartbeatRequest`, then replaces the simple ops table with `HeartbeatRequestMsgEx_Ops` so incoming processing sends a heartbeat response.

Control flow is inline init plus receive behavior in the `.c` file. State is only inherited simple-message state. Dependencies are `SimpleMsg.h`. Integration points are datagram/stream listeners that dispatch heartbeat requests to produce `HeartbeatMsgEx` responses. Risks are forgetting the ops override, which would leave default no-op/false processing, and protocol changes adding request payload. Test signals are dispatch invoking `__HeartbeatRequestMsgEx_processIncoming` and response message type `NETMSGTYPE_Heartbeat`.
