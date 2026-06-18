# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsRespMsg.h

## Purpose
Defines `MapTargetsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_MapTargetsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MapTargetsRespMsg` derives from `public NetMessageSerdes<MapTargetsRespMsg>` and uses `BaseType(NETMSGTYPE_MapTargetsResp)` or an equivalent base constructor. Constructors include `MapTargetsRespMsg(const std::map<uint16_t, FhgfsOpsErr>& results): BaseType(NETMSGTYPE_MapTargetsResp), results(&results)`; `MapTargetsRespMsg(): BaseType(NETMSGTYPE_MapTargetsResp)`. Serialization writes `backedPtr(obj->results, obj->parsed.results)`. Notable accessors/helpers include `getResults()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `MapTargetsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_MapTargetsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MapTargetsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
