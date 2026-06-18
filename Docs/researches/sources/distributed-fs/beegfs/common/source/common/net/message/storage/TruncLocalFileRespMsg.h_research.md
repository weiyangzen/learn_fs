# sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileRespMsg.h

## Purpose
Defines `TruncLocalFileRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_TruncLocalFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`TruncLocalFileRespMsg` derives from `public NetMessageSerdes<TruncLocalFileRespMsg>` and uses `BaseType(NETMSGTYPE_TruncLocalFileResp)` or an equivalent base constructor. Constructors include `TruncLocalFileRespMsg(FhgfsOpsErr result, int64_t filesize, int64_t allocedBlocks, int64_t modificationTimeSecs, int64_t lastAccessTimeSecs, uint64_t storageVersion) : BaseType(NETMSGTYPE_TruncLocalFileResp)`; `TruncLocalFileRespMsg() : BaseType(NETMSGTYPE_TruncLocalFileResp)`. Serialization writes `filesize`, `allocedBlocks`, `modificationTimeSecs`, `lastAccessTimeSecs`, `storageVersion`, `result`. Notable accessors/helpers include `getResult()`, `getFileSize()`, `getAllocedBlocks()`, `getModificationTimeSecs()`, `getLastAccessTimeSecs()`, `getStorageVersion()`. Declared payload/backing members include `int32_t result`, `int64_t filesize`, `int64_t modificationTimeSecs`, `int64_t lastAccessTimeSecs`, `uint64_t storageVersion`.

## Control Flow
Sender-side code builds `TruncLocalFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_TruncLocalFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_TruncLocalFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
