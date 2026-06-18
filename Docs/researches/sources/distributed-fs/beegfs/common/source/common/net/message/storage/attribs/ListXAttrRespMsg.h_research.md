# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/ListXAttrRespMsg.h

## Purpose
Defines `ListXAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_ListXAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`ListXAttrRespMsg` derives from `public NetMessageSerdes<ListXAttrRespMsg>` and uses `BaseType(NETMSGTYPE_ListXAttrResp)` or an equivalent base constructor. Constructors include `ListXAttrRespMsg(const StringVector& value, int size, int returnCode) : BaseType(NETMSGTYPE_ListXAttrResp), value(value), size(size), returnCode(returnCode)`; `ListXAttrRespMsg() : BaseType(NETMSGTYPE_ListXAttrResp)`. Serialization writes `value`, `size`, `returnCode`. Notable accessors/helpers include `getValue()`, `getReturnCode()`, `getSize()`. Declared payload/backing members include `StringVector value`, `int32_t size`, `int32_t returnCode`.

## Control Flow
Sender-side code builds `ListXAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/app/log/LogContext.h`, `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_ListXAttrResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListXAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
