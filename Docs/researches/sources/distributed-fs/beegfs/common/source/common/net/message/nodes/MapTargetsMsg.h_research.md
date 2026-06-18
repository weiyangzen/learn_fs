# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsMsg.h

## Purpose
Defines `MapTargetsMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_MapTargets`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`MapTargetsMsg` derives from `public AcknowledgeableMsgSerdes<MapTargetsMsg>` and uses `BaseType(NETMSGTYPE_MapTargets)` or an equivalent base constructor. Constructors include `MapTargetsMsg(const std::map<uint16_t, StoragePoolId>& targets, NumNodeID nodeID): BaseType(NETMSGTYPE_MapTargets), nodeID(nodeID), targets(&targets)`; `MapTargetsMsg() : BaseType(NETMSGTYPE_MapTargets)`. Serialization writes `backedPtr(obj->targets, obj->parsed.targets)`, `nodeID`. Notable accessors/helpers include `serializeAckID()`, `getNodeID()`, `getTargets()`. Declared payload/backing members include `NumNodeID nodeID`.

## Control Flow
Sender-side code builds `MapTargetsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/NumNodeID.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_MapTargets`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MapTargets`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
