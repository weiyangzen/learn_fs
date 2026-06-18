# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/HeartbeatMsg.h

## Purpose
Defines `HeartbeatMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_Heartbeat`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`HeartbeatMsg` derives from `public AcknowledgeableMsgSerdes<HeartbeatMsg>` and uses `BaseType(NETMSGTYPE_Heartbeat)` or an equivalent base constructor. Constructors include `HeartbeatMsg(const std::string& nodeID, NumNodeID nodeNumID, NodeType nodeType, NicAddressList* nicList) : BaseType(NETMSGTYPE_Heartbeat)`; `HeartbeatMsg() : BaseType(NETMSGTYPE_Heartbeat)`. Serialization writes `instanceVersion`, `nicListVersion`, `nodeType`, `nodeID`, `nodeNumID`, `rootNumID`, `rootIsBuddyMirrored`, `portUDP`, `portTCP`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `machineUUID`. Notable accessors/helpers include `serializeAckID()`, `getNicList()`, `getNodeID()`, `getNodeNumID()`, `getNodeType()`, `getRootNumID()`, `setRootNumID()`, `getRootIsBuddyMirrored()`, `setRootIsBuddyMirrored()`, `setPorts()`, `setMachineUUID()`, `getPortUDP()`, and additional getters/setters. Declared payload/backing members include `std::string nodeID`, `std::string machineUUID`, `int32_t nodeType`, `NumNodeID nodeNumID`, `NumNodeID rootNumID`, `bool rootIsBuddyMirrored`, `uint64_t instanceVersion`, `uint64_t nicListVersion`, `uint16_t portUDP`, `uint16_t portTCP`, `NicAddressList* nicList`, `NicAddressList nicList`.

## Control Flow
Sender-side code builds `HeartbeatMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/net/sock/NetworkInterfaceCard.h`, `common/nodes/Node.h`, `common/Common.h`, `iostream`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_Heartbeat`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_Heartbeat`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
