# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/SetChannelDirectMsg.h

## Research
`SetChannelDirectMsg.h` defines `NETMSGTYPE_SetChannelDirect` as a thin `SimpleIntMsg` wrapper. It can be initialized empty or from an integer value, which higher layers use to request or signal direct-channel behavior.

Control flow is inline delegation to `SimpleIntMsg` constructors. State is a single integer payload with no owned memory. Dependencies are `SimpleIntMsg.h`. Integration points are channel setup/control paths that need a compact value-bearing message without custom payload code. Risks are the integer value being semantically opaque in this file, so invalid modes must be checked by the receiver. Test signals are channel setup messages carrying expected values and default `NetMessage_processIncoming` preventing accidental unhandled receive-side processing in the client.
