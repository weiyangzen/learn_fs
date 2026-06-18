# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolRespMsg.h

## Purpose
Defines `AddStoragePoolRespMsg`, the response payload wrapper for BeeGFS storage pool management RPCs using `NETMSGTYPE_AddStoragePoolResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`AddStoragePoolRespMsg` derives from `public NetMessageSerdes<AddStoragePoolRespMsg>` and uses `BaseType(NETMSGTYPE_AddStoragePoolResp)` or an equivalent base constructor. Constructors include `AddStoragePoolRespMsg(FhgfsOpsErr result, StoragePoolId poolId) : BaseType(NETMSGTYPE_AddStoragePoolResp), result(result), poolId(poolId)`; `AddStoragePoolRespMsg() : BaseType(NETMSGTYPE_AddStoragePoolResp)`. Serialization writes `result`, `poolId`. Notable accessors/helpers include `getResult()`, `getPoolId()`. Declared payload/backing members include `FhgfsOpsErr result`, `StoragePoolId poolId`.

## Control Flow
Sender-side code builds `AddStoragePoolRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageErrors.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_AddStoragePoolResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_AddStoragePoolResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
