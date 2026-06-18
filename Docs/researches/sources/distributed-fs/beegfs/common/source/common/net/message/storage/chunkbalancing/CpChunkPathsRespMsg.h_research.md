# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/CpChunkPathsRespMsg.h

## Purpose
Defines `CpChunkPathsRespMsg`, the response payload wrapper for BeeGFS chunk balancing RPCs using `NETMSGTYPE_CpChunkPathsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`CpChunkPathsRespMsg` derives from `public NetMessageSerdes<CpChunkPathsRespMsg>` and uses `BaseType(NETMSGTYPE_CpChunkPathsResp)` or an equivalent base constructor. Constructors include `CpChunkPathsRespMsg(FhgfsOpsErr result ) : BaseType(NETMSGTYPE_CpChunkPathsResp)`; `CpChunkPathsRespMsg() : BaseType(NETMSGTYPE_CpChunkPathsResp)`. Serialization writes `result`. Notable accessors/helpers include `getResult()`. Declared payload/backing members include `int32_t result`.

## Control Flow
Sender-side code builds `CpChunkPathsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_CpChunkPathsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CpChunkPathsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
