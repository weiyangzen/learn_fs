# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.c

## Research
`SimpleInt64Msg.c` implements payload ops for messages that carry one signed 64-bit integer. `SimpleInt64Msg_Ops` uses normal serialization/deserialization functions, default incoming processing, and default feature-mask handling. `SimpleInt64Msg_serializePayload` writes `value` with `Serialization_serializeInt64`; `SimpleInt64Msg_deserializePayload` reads it with `Serialization_deserializeInt64`.

Control flow is a single field round trip and returns the serializer boolean on input. State is just the inherited `NetMessage` plus `value`, owned by the containing concrete message. Dependencies are `SimpleInt64Msg.h`, `NetMessage`, and `Serialization`. Integration points include 64-bit-valued responses such as fsync-local-file results and auth hash transport variants. Risks are signedness expectations when callers use uint64-style values through this signed container and lack of range-level validation. Test signals are payload-length correctness, negative and large-value round trips, and derived response classes reading expected `FhgfsOpsErr`/byte-count semantics.
