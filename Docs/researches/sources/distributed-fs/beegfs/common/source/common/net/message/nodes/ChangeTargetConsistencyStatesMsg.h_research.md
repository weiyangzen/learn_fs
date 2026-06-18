# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/ChangeTargetConsistencyStatesMsg.h

## Purpose
Defines `ChangeTargetConsistencyStatesMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_ChangeTargetConsistencyStates`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ChangeTargetConsistencyStatesMsg` derives from `public AcknowledgeableMsgSerdes<ChangeTargetConsistencyStatesMsg>` and uses `BaseType(NETMSGTYPE_ChangeTargetConsistencyStates)` or an equivalent base constructor. Constructors include `ChangeTargetConsistencyStatesMsg(NodeType nodeType, UInt16List* targetIDs, UInt8List* oldStates, UInt8List* newStates) : BaseType(NETMSGTYPE_ChangeTargetConsistencyStates), nodeType(nodeType), targetIDs(targetIDs), oldStates(oldStates), newStates(newStates)`; `ChangeTargetConsistencyStatesMsg() : BaseType(NETMSGTYPE_ChangeTargetConsistencyStates)`. Serialization writes `nodeType`, `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`, `backedPtr(obj->oldStates, obj->parsed.oldStates)`, `backedPtr(obj->newStates, obj->parsed.newStates)`. Notable accessors/helpers include `serializeAckID()`, `getNodeType()`, `getTargetIDs()`, `getOldStates()`, `getNewStates()`. Declared payload/backing members include `int32_t nodeType`, `UInt16List* targetIDs`, `UInt8List* oldStates`, `UInt8List* newStates`, `UInt16List targetIDs`, `UInt8List oldStates`, `UInt8List newStates`.

## Control Flow
Sender-side code builds `ChangeTargetConsistencyStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_ChangeTargetConsistencyStates`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ChangeTargetConsistencyStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
