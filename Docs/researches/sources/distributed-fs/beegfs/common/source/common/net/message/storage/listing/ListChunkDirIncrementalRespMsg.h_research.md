# sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalRespMsg.h

## Purpose
Defines `ListChunkDirIncrementalRespMsg`, the response payload wrapper for BeeGFS directory and chunk listing RPCs using `NETMSGTYPE_ListChunkDirIncrementalResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`ListChunkDirIncrementalRespMsg` derives from `public NetMessageSerdes<ListChunkDirIncrementalRespMsg>` and uses `BaseType(NETMSGTYPE_ListChunkDirIncrementalResp)` or an equivalent base constructor. Constructors include `ListChunkDirIncrementalRespMsg(FhgfsOpsErr result, StringList* names, IntList* entryTypes, int64_t newOffset) : BaseType(NETMSGTYPE_ListChunkDirIncrementalResp)`; `ListChunkDirIncrementalRespMsg() : BaseType(NETMSGTYPE_ListChunkDirIncrementalResp)`. Serialization writes `result`, `newOffset`, `backedPtr(obj->names, obj->parsed.names)`, `backedPtr(obj->entryTypes, obj->parsed.entryTypes)`. Notable accessors/helpers include `getNames()`, `getEntryTypes()`, `getResult()`, `getNewOffset()`. Declared payload/backing members include `int32_t result`, `int64_t newOffset`, `StringList* names`, `IntList* entryTypes`, `StringList names`, `IntList entryTypes`.

## Control Flow
Sender-side code builds `ListChunkDirIncrementalRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the directory and chunk listing code path that handles `NETMSGTYPE_ListChunkDirIncrementalResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; offset cursors can repeat or skip records if callers mishandle continuation.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListChunkDirIncrementalResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
