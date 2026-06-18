# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveNodeMsg.h

## Purpose
Defines `RemoveNodeMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RemoveNode`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveNodeMsg` derives from `public AcknowledgeableMsgSerdes<RemoveNodeMsg>` and uses `BaseType(NETMSGTYPE_RemoveNode)` or an equivalent base constructor. Constructors include `RemoveNodeMsg(NumNodeID nodeNumID, NodeType nodeType) : BaseType(NETMSGTYPE_RemoveNode)`; `RemoveNodeMsg() : BaseType(NETMSGTYPE_RemoveNode)`. Serialization writes `nodeType`, `nodeNumID`. Notable accessors/helpers include `serializeAckID()`, `getNodeNumID()`, `getNodeType()`. Declared payload/backing members include `NumNodeID nodeNumID`, `int16_t nodeType`.

## Control Flow
Sender-side code builds `RemoveNodeMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RemoveNode`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveNode`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
