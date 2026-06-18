# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetMirrorBuddyGroupMsg.h

## Purpose
Defines `SetMirrorBuddyGroupMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_SetMirrorBuddyGroup`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetMirrorBuddyGroupMsg` derives from `public AcknowledgeableMsgSerdes<SetMirrorBuddyGroupMsg>` and uses `BaseType(NETMSGTYPE_SetMirrorBuddyGroup)` or an equivalent base constructor. Constructors include `SetMirrorBuddyGroupMsg(NodeType nodeType, uint16_t primaryTargetID, uint16_t secondaryTargetID, uint16_t buddyGroupID = 0, bool allowUpdate = false) : BaseType(NETMSGTYPE_SetMirrorBuddyGroup), nodeType(nodeType), primaryTargetID(primaryTargetID), secondaryTargetID(secondaryTargetID), buddyGroupID(buddyGroupID), allowUpdate(allowUpdate)`; `SetMirrorBuddyGroupMsg() : BaseType(NETMSGTYPE_SetMirrorBuddyGroup)`. Serialization writes `nodeType`, `primaryTargetID`, `secondaryTargetID`, `buddyGroupID`, `allowUpdate`. Notable accessors/helpers include `serializeAckID()`, `getNodeType()`, `getPrimaryTargetID()`, `getSecondaryTargetID()`, `getBuddyGroupID()`, `getAllowUpdate()`. Declared payload/backing members include `int32_t nodeType`, `uint16_t primaryTargetID`, `uint16_t secondaryTargetID`, `uint16_t buddyGroupID`, `bool allowUpdate`.

## Control Flow
Sender-side code builds `SetMirrorBuddyGroupMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_SetMirrorBuddyGroup`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetMirrorBuddyGroup`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
