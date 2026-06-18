# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsRespMsg.h

## Purpose
Defines `GetClientStatsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetClientStatsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetClientStatsRespMsg` derives from `public NetMessageSerdes<GetClientStatsRespMsg>` and uses `BaseType(NETMSGTYPE_GetClientStatsResp)` or an equivalent base constructor. Constructors include `GetClientStatsRespMsg(UInt64Vector* statsVec) : BaseType(NETMSGTYPE_GetClientStatsResp)`; `GetClientStatsRespMsg() : BaseType(NETMSGTYPE_GetClientStatsResp)`. Serialization writes `backedPtr(obj->statsVec, obj->parsed.statsVec)`. Notable accessors/helpers include `getStatsVector()`. Declared payload/backing members include `UInt64Vector* statsVec`, `UInt64Vector statsVec`.

## Control Flow
Sender-side code builds `GetClientStatsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/HighResolutionStats.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetClientStatsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetClientStatsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
