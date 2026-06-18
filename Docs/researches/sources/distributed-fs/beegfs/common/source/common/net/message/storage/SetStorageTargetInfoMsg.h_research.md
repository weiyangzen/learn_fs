# sources/distributed-fs/beegfs/common/source/common/net/message/storage/SetStorageTargetInfoMsg.h

## Purpose
Defines `SetStorageTargetInfoMsg`, a BeeGFS storage target operation command message using `NETMSGTYPE_SetStorageTargetInfo`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetStorageTargetInfoMsg` derives from `public NetMessageSerdes<SetStorageTargetInfoMsg>` and uses `BaseType(NETMSGTYPE_SetStorageTargetInfo)` or an equivalent base constructor. Constructors include `SetStorageTargetInfoMsg(NodeType nodeType, StorageTargetInfoList *targetInfoList) : BaseType(NETMSGTYPE_SetStorageTargetInfo)`; `SetStorageTargetInfoMsg() : BaseType(NETMSGTYPE_SetStorageTargetInfo)`. Serialization writes `nodeType`, `backedPtr(obj->targetInfoList, obj->parsed.targetInfoList)`. Notable accessors/helpers include `getNodeType()`, `getStorageTargetInfos()`. Declared payload/backing members include `StorageTargetInfoList* targetInfoList`, `int32_t nodeType`, `StorageTargetInfoList targetInfoList`.

## Control Flow
Sender-side code builds `SetStorageTargetInfoMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/storage/StorageTargetInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_SetStorageTargetInfo`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetStorageTargetInfo`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
