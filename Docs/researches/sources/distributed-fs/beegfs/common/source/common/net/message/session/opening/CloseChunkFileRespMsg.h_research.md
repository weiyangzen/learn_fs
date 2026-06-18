# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileRespMsg.h

## Purpose
Defines `CloseChunkFileRespMsg`, the response payload wrapper for BeeGFS file open and close session RPCs using `NETMSGTYPE_CloseChunkFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`CloseChunkFileRespMsg` derives from `public NetMessageSerdes<CloseChunkFileRespMsg>` and uses `BaseType(NETMSGTYPE_CloseChunkFileResp)` or an equivalent base constructor. Constructors include `CloseChunkFileRespMsg(FhgfsOpsErr result, int64_t filesize, int64_t allocedBlocks, int64_t modificationTimeSecs, int64_t lastAccessTimeSecs, uint64_t storageVersion) : BaseType(NETMSGTYPE_CloseChunkFileResp)`; `CloseChunkFileRespMsg() : BaseType(NETMSGTYPE_CloseChunkFileResp)`. Serialization writes `filesize`, `allocedBlocks`, `modificationTimeSecs`, `lastAccessTimeSecs`, `storageVersion`, `result`. Notable accessors/helpers include `getResult()`, `getFileSize()`, `getAllocedBlocks()`, `getModificationTimeSecs()`, `getLastAccessTimeSecs()`, `getStorageVersion()`. Declared payload/backing members include `int32_t result`, `int64_t filesize`, `int64_t modificationTimeSecs`, `int64_t lastAccessTimeSecs`, `uint64_t storageVersion`.

## Control Flow
Sender-side code builds `CloseChunkFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_CloseChunkFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CloseChunkFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
