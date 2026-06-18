# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RemoveStoragePoolMsg.h

## Purpose
Defines `RemoveStoragePoolMsg`, a BeeGFS storage pool management command message using `NETMSGTYPE_RemoveStoragePool`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveStoragePoolMsg` derives from `public NetMessageSerdes<RemoveStoragePoolMsg>` and uses `BaseType(NETMSGTYPE_RemoveStoragePool)` or an equivalent base constructor. Constructors include `RemoveStoragePoolMsg(StoragePoolId poolId) : BaseType(NETMSGTYPE_RemoveStoragePool), poolId(poolId)`; `RemoveStoragePoolMsg() : BaseType(NETMSGTYPE_RemoveStoragePool)`. Serialization writes `poolId`. Declared payload/backing members include `StoragePoolId poolId`.

## Control Flow
Sender-side code builds `RemoveStoragePoolMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_RemoveStoragePool`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveStoragePool`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
