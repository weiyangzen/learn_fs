# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h

## Purpose
Defines `GetStatesAndBuddyGroupsMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetStatesAndBuddyGroups`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetStatesAndBuddyGroupsMsg` derives from `public NetMessageSerdes<GetStatesAndBuddyGroupsMsg>` and uses `BaseType(NETMSGTYPE_GetStatesAndBuddyGroups)` or an equivalent base constructor. Constructors include `GetStatesAndBuddyGroupsMsg(NodeType nodeType) : BaseType(NETMSGTYPE_GetStatesAndBuddyGroups), nodeType(nodeType), requestedByClientID(NumNodeID(0))`; `GetStatesAndBuddyGroupsMsg() : BaseType(NETMSGTYPE_GetStatesAndBuddyGroups)`. Serialization writes `nodeType`, `requestedByClientID`. Notable accessors/helpers include `getNodeType()`, `getRequestedByClientID()`. Declared payload/backing members include `int32_t nodeType`, `NumNodeID requestedByClientID`.

## Control Flow
Sender-side code builds `GetStatesAndBuddyGroupsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/nodes/NumNodeID.h`, `common/net/message/SimpleIntMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetStatesAndBuddyGroups`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetStatesAndBuddyGroups`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
