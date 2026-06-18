# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveBuddyGroupMsg.h

## Purpose
Defines `RemoveBuddyGroupMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RemoveBuddyGroup`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveBuddyGroupMsg` derives from `public NetMessageSerdes<RemoveBuddyGroupMsg>` and uses `BaseType(NETMSGTYPE_RemoveBuddyGroup)` or an equivalent base constructor. Constructors include `RemoveBuddyGroupMsg(NodeType type, uint16_t groupID, bool checkOnly, bool force): BaseType(NETMSGTYPE_RemoveBuddyGroup), type(type), groupID(groupID), checkOnly(checkOnly), force(force)`; `RemoveBuddyGroupMsg() : BaseType(NETMSGTYPE_RemoveNode)`. Serialization writes `type`, `groupID`, `checkOnly`, `force`. Declared payload/backing members include `NodeType type`, `uint16_t groupID`, `bool checkOnly`, `bool force`.

## Control Flow
Sender-side code builds `RemoveBuddyGroupMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RemoveBuddyGroup`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveBuddyGroup`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
