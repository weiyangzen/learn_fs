# sources/distributed-fs/beegfs/common/source/common/net/message/storage/GetHighResStatsRespMsg.h

## Purpose
Defines `GetHighResStatsRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_GetHighResStatsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetHighResStatsRespMsg` derives from `public NetMessageSerdes<GetHighResStatsRespMsg>` and uses `BaseType(NETMSGTYPE_GetHighResStatsResp)` or an equivalent base constructor. Constructors include `GetHighResStatsRespMsg(HighResStatsList* statsList) : BaseType(NETMSGTYPE_GetHighResStatsResp)`; `GetHighResStatsRespMsg() : BaseType(NETMSGTYPE_GetHighResStatsResp)`. Serialization writes `backedPtr(obj->statsList, obj->parsed.statsList)`. Notable accessors/helpers include `getStatsList()`. Declared payload/backing members include `HighResStatsList* statsList`, `HighResStatsList statsList`.

## Control Flow
Sender-side code builds `GetHighResStatsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/HighResolutionStats.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_GetHighResStatsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetHighResStatsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
