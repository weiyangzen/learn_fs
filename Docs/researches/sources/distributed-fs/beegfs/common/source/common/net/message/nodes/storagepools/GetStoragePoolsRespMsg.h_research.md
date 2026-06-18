# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/GetStoragePoolsRespMsg.h

## Purpose
Defines `GetStoragePoolsRespMsg`, the response payload wrapper for BeeGFS storage pool management RPCs using `NETMSGTYPE_GetStoragePoolsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetStoragePoolsRespMsg` derives from `public NetMessageSerdes<GetStoragePoolsRespMsg>` and uses `BaseType(NETMSGTYPE_GetStoragePoolsResp)` or an equivalent base constructor. Constructors include `GetStoragePoolsRespMsg(StoragePoolPtrVec* pools): BaseType(NETMSGTYPE_GetStoragePoolsResp), pools(pools)`; `GetStoragePoolsRespMsg(): BaseType(NETMSGTYPE_GetStoragePoolsResp)`. Serialization writes `backedPtr(obj->pools, obj->parsed.pools)`. Notable accessors/helpers include `getStoragePools()`. Declared payload/backing members include `StoragePoolPtrVec* pools`, `StoragePoolPtrVec pools`.

## Control Flow
Sender-side code builds `GetStoragePoolsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StoragePool.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_GetStoragePoolsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetStoragePoolsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
