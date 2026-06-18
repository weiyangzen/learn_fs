# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolMsg.h

## Purpose
Defines `AddStoragePoolMsg`, a BeeGFS storage pool management command message using `NETMSGTYPE_AddStoragePool`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`AddStoragePoolMsg` derives from `public NetMessageSerdes<AddStoragePoolMsg>` and uses `BaseType(NETMSGTYPE_AddStoragePool)` or an equivalent base constructor. Constructors include `AddStoragePoolMsg(StoragePoolId poolId, const std::string& description, const UInt16Set* targets, const UInt16Set* buddyGroups): BaseType(NETMSGTYPE_AddStoragePool), poolId(poolId), description(description), targetsPtr(targets), buddyGroupsPtr(buddyGroups)`; `AddStoragePoolMsg(): BaseType(NETMSGTYPE_AddStoragePool)`. Serialization writes `poolId`, `description`, `backedPtr(obj->targetsPtr, obj->targets)`, `backedPtr(obj->buddyGroupsPtr, obj->buddyGroups)`. Declared payload/backing members include `StoragePoolId poolId`, `std::string description`, `const UInt16Set* targetsPtr`, `UInt16Set targets`, `const UInt16Set* buddyGroupsPtr`, `UInt16Set buddyGroups`.

## Control Flow
Sender-side code builds `AddStoragePoolMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/storage/StoragePoolId.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_AddStoragePool`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_AddStoragePool`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
