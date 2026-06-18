# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RemoveInodesRespMsg.h

## Purpose
Defines `RemoveInodesRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_RemoveInodesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RemoveInodesRespMsg` derives from `public NetMessageSerdes<RemoveInodesRespMsg>` and uses `BaseType(NETMSGTYPE_RemoveInodesResp)` or an equivalent base constructor. Constructors include `RemoveInodesRespMsg(StringList failedEntryIDList) : BaseType(NETMSGTYPE_RemoveInodesResp), failedEntryIDList(std::move(failedEntryIDList))`; `RemoveInodesRespMsg() : BaseType(NETMSGTYPE_RemoveInodesResp)`. Serialization writes `failedEntryIDList`. Declared payload/backing members include `StringList failedEntryIDList`.

## Control Flow
Sender-side code builds `RemoveInodesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageDefinitions.h`, `common/toolkit/ListTk.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RemoveInodesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveInodesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
