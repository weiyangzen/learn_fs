# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeMsg.h

## Purpose
Defines `RegisterNodeMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RegisterNode`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RegisterNodeMsg` derives from `public NetMessageSerdes<RegisterNodeMsg>` and uses `BaseType(NETMSGTYPE_RegisterNode)` or an equivalent base constructor. Constructors include `RegisterNodeMsg(const std::string& nodeID, NumNodeID nodeNumID, NodeType nodeType, NicAddressList* nicList, uint16_t portUDP, uint16_t portTCP) : BaseType(NETMSGTYPE_RegisterNode)`; `RegisterNodeMsg() : BaseType(NETMSGTYPE_RegisterNode)`. Serialization writes `instanceVersion`, `nicListVersion`, `nodeID`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `nodeType`, `nodeNumID`, `rootNumID`, `rootIsBuddyMirrored`, `portUDP`, `portTCP`, `machineUUID`. Notable accessors/helpers include `getNicList()`, `getNodeID()`, `getNodeNumID()`, `getNodeType()`, `getRootNumID()`, `setRootNumID()`, `getRootIsBuddyMirrored()`, `setRootIsBuddyMirrored()`, `setMachineUUID()`, `getPortUDP()`, `getPortTCP()`. Declared payload/backing members include `std::string nodeID`, `std::string machineUUID`, `int32_t nodeType`, `NumNodeID nodeNumID`, `NumNodeID rootNumID`, `bool rootIsBuddyMirrored`, `uint64_t instanceVersion`, `uint64_t nicListVersion`, `uint16_t portUDP`, `uint16_t portTCP`, `NicAddressList* nicList`, `NicAddressList nicList`.

## Control Flow
Sender-side code builds `RegisterNodeMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/sock/NetworkInterfaceCard.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RegisterNode`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RegisterNode`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
