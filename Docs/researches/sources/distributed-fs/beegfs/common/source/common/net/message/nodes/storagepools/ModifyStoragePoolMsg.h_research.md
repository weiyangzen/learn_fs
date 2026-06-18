# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/ModifyStoragePoolMsg.h

## Purpose
Defines `ModifyStoragePoolMsg`, a BeeGFS storage pool management command message using `NETMSGTYPE_ModifyStoragePool`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ModifyStoragePoolMsg` derives from `public NetMessageSerdes<ModifyStoragePoolMsg>` and uses `BaseType(NETMSGTYPE_ModifyStoragePool)` or an equivalent base constructor. Constructors include `ModifyStoragePoolMsg(StoragePoolId poolId, const UInt16Vector* addTargets, const UInt16Vector* rmTargets, const UInt16Vector* addBuddyGroups, const UInt16Vector* rmBuddyGroups, const std::string* newDescription) : BaseType(NETMSGTYPE_ModifyStoragePool), poolId(poolId), addTargets(addTargets), rmTargets(rmTargets), addBuddyGroups(addBuddyGroups), rmBuddyGroups(rmBuddyGroups), newDescription(newDescription)`; `ModifyStoragePoolMsg(): BaseType(NETMSGTYPE_ModifyStoragePool), addTargets(nullptr), rmTargets(nullptr), addBuddyGroups(nullptr), rmBuddyGroups(nullptr), newDescription(nullptr)`. Serialization writes `poolId`, `backedPtr(obj->newDescription, obj->parsed.newDescription)`, `backedPtr(obj->addTargets, obj->parsed.addTargets)`, `backedPtr(obj->rmTargets, obj->parsed.rmTargets)`, `backedPtr(obj->addBuddyGroups, obj->parsed.addBuddyGroups)`, `backedPtr(obj->rmBuddyGroups, obj->parsed.rmBuddyGroups)`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `static const unsigned HAS_NEWDESCRIPTION`, `static const unsigned HAS_ADDTARGETS`, `static const unsigned HAS_RMTARGETS`, `static const unsigned HAS_ADDBUDDYGROUPS`, `static const unsigned HAS_RMBUDDYGROUPS`, `StoragePoolId poolId`, `const UInt16Vector* addTargets`, `const UInt16Vector* rmTargets`, `const UInt16Vector* addBuddyGroups`, `const UInt16Vector* rmBuddyGroups`, `const std::string* newDescription`, `UInt16Vector addTargets`, `UInt16Vector rmTargets`, `UInt16Vector addBuddyGroups`, plus additional backing fields.

## Control Flow
Sender-side code builds `ModifyStoragePoolMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_ModifyStoragePool`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ModifyStoragePool`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
