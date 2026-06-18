# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetEntryInfoRespMsg.h

## Purpose
Defines `GetEntryInfoRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_GetEntryInfoResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetEntryInfoRespMsg` derives from `public NetMessageSerdes<GetEntryInfoRespMsg>` and uses `BaseType(NETMSGTYPE_GetEntryInfoResp)` or an equivalent base constructor. Constructors include `GetEntryInfoRespMsg(FhgfsOpsErr result, StripePattern* pattern, uint16_t mirrorNodeID, PathInfo* pathInfoPtr, RemoteStorageTarget* rst, uint32_t numSessionsRead = 0, uint32_t numSessionsWrite = 0, uint8_t dataState = 0) : BaseType(NETMSGTYPE_GetEntryInfoResp)`; `GetEntryInfoRespMsg() : BaseType(NETMSGTYPE_GetEntryInfoResp)`. Serialization writes `result`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `backedPtr(obj->rstPtr, obj->rst)`, `mirrorNodeID`, `numSessionsRead`, `numSessionsWrite`, `fileDataState`. Notable accessors/helpers include `getPattern()`, `getResult()`, `getMirrorNodeID()`, `getPathInfo()`, `getRemoteStorageTarget()`, `getNumSessionsRead()`, `getNumSessionsWrite()`, `getFileDataState()`. Declared payload/backing members include `int32_t result`, `uint32_t numSessionsRead`, `uint32_t numSessionsWrite`, `uint8_t  fileDataState`, `StripePattern* pattern`, `PathInfo* pathInfoPtr`, `RemoteStorageTarget* rstPtr`, `RemoteStorageTarget rst`, `std::unique_ptr<StripePattern> pattern`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `GetEntryInfoRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/StripePattern.h`, `common/storage/RemoteStorageTarget.h`, `common/storage/StorageErrors.h`, `common/storage/PathInfo.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetEntryInfoResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetEntryInfoResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
