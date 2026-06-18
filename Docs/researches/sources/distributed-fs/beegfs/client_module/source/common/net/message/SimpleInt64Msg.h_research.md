# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.h

## Research
`SimpleInt64Msg.h` declares the reusable one-int64 message wrapper. `struct SimpleInt64Msg` embeds `NetMessage` and an `int64_t value`; inline initializers set the message type and optionally the value, and `SimpleInt64Msg_getValue` returns the stored scalar. The ops are implemented in the `.c` file.

Control flow is construction-only in this header. State is non-owning and fixed-size, with no heap allocations or persistence. Dependencies are `NetMessage.h` and the shared ops object. Integration points are concrete message typedef wrappers that need a simple 64-bit result or token without custom payload code. Risks are treating the wrapper as owning external data, using it for unsigned protocol values without clear conversion, or changing message type after length caching. Test signals are derived message initializers setting the right `NETMSGTYPE_*`, and deserialization populating `value` for response handlers.
