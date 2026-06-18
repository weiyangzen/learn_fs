# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkDirRespMsg.h

## Purpose
Defines `MkDirRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MkDirResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MkDirRespMsg` derives from `public NetMessageSerdes<MkDirRespMsg>` and uses `BaseType(NETMSGTYPE_MkDirResp)` or an equivalent base constructor. Constructors include `MkDirRespMsg(int result, EntryInfo* entryInfo) : BaseType(NETMSGTYPE_MkDirResp)`; `MkDirRespMsg() : BaseType(NETMSGTYPE_MkDirResp)`. Serialization writes `result`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`. Notable accessors/helpers include `getResult()`, `getEntryInfo()`. Declared payload/backing members include `int32_t result`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `MkDirRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkDirResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkDirResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
