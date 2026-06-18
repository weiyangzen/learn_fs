# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetTargetConsistencyStatesMsg.h

## Purpose
Defines `SetTargetConsistencyStatesMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_SetTargetConsistencyStates`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetTargetConsistencyStatesMsg` derives from `public AcknowledgeableMsgSerdes<SetTargetConsistencyStatesMsg>` and uses `BaseType(NETMSGTYPE_SetTargetConsistencyStates)` or an equivalent base constructor. Constructors include `SetTargetConsistencyStatesMsg(NodeType nodeType, UInt16List* targetIDs, UInt8List* states, bool setOnline) : BaseType(NETMSGTYPE_SetTargetConsistencyStates)`; `SetTargetConsistencyStatesMsg() : BaseType(NETMSGTYPE_SetTargetConsistencyStates)`. Serialization writes `nodeType`, `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`, `backedPtr(obj->states, obj->parsed.states)`, `setOnline`. Notable accessors/helpers include `serializeAckID()`, `getNodeType()`, `getTargetIDs()`, `getStates()`, `getSetOnline()`. Declared payload/backing members include `int nodeType`, `UInt16List* targetIDs`, `UInt8List* states`, `bool setOnline`, `UInt16List targetIDs`, `UInt8List states`.

## Control Flow
Sender-side code builds `SetTargetConsistencyStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_SetTargetConsistencyStates`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetTargetConsistencyStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
