# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetLocalAttrRespMsg.h

## Purpose
Defines `SetLocalAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_SetLocalAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetLocalAttrRespMsg` derives from `public NetMessageSerdes<SetLocalAttrRespMsg>` and uses `BaseType(NETMSGTYPE_SetLocalAttrResp)` or an equivalent base constructor. Constructors include `SetLocalAttrRespMsg(FhgfsOpsErr result, DynamicFileAttribs& dynamicAttribs) : BaseType(NETMSGTYPE_SetLocalAttrResp), result(result), filesize(dynamicAttribs.fileSize), numBlocks(dynamicAttribs.numBlocks), modificationTimeSecs(dynamicAttribs.modificationTimeSecs), lastAccessTimeSecs(dynamicAttribs.lastAccessTimeSecs), storageVersion(dynamicAttribs.storageVersion)`; `SetLocalAttrRespMsg(FhgfsOpsErr result) : BaseType(NETMSGTYPE_SetLocalAttrResp), result(result), filesize(0), numBlocks(0), modificationTimeSecs(0), lastAccessTimeSecs(0), storageVersion(0)`; `SetLocalAttrRespMsg() : BaseType(NETMSGTYPE_SetLocalAttrResp)`. Serialization writes `filesize`, `numBlocks`, `modificationTimeSecs`, `lastAccessTimeSecs`, `storageVersion`, `result`. Notable accessors/helpers include `getResult()`, `getDynamicAttribs()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `FhgfsOpsErr result`, `int64_t filesize`, `int64_t numBlocks`, `int64_t modificationTimeSecs`, `int64_t lastAccessTimeSecs`, `uint64_t storageVersion`.

## Control Flow
Sender-side code builds `SetLocalAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/DynamicFileAttribs.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetLocalAttrResp`. Feature flags: `SETLOCALATTRRESPMSG_FLAG_HAS_ATTRS`=1.

## Risks And Edge Cases
Feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetLocalAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
