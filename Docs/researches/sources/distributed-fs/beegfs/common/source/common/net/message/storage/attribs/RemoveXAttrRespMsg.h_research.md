# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RemoveXAttrRespMsg.h

## Purpose
Defines `RemoveXAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_RemoveXAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RemoveXAttrRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RemoveXAttrResp)` or an equivalent base constructor. Constructors include `RemoveXAttrRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_RemoveXAttrResp, result)`; `RemoveXAttrRespMsg() : SimpleIntMsg(NETMSGTYPE_RemoveXAttrResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RemoveXAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_RemoveXAttrResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveXAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
