# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodesRespMsg.h

## Purpose
Defines `GetNodesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetNodesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetNodesRespMsg` derives from `public NetMessageSerdes<GetNodesRespMsg>` and uses `BaseType(NETMSGTYPE_GetNodesResp)` or an equivalent base constructor. Constructors include `GetNodesRespMsg(NumNodeID rootNumID, bool rootIsBuddyMirrored, std::vector<NodeHandle>& nodeList) : BaseType(NETMSGTYPE_GetNodesResp)`; `GetNodesRespMsg() : BaseType(NETMSGTYPE_GetNodesResp)`. Serialization writes `backedPtr(obj->nodeList, obj->parsed.nodeList)`, `rootNumID`, `rootIsBuddyMirrored`. Notable accessors/helpers include `getNodeList()`, `getRootNumID()`, `getRootIsBuddyMirrored()`. Declared payload/backing members include `NumNodeID rootNumID`, `bool rootIsBuddyMirrored`, `std::vector<NodeHandle>* nodeList`, `std::vector<NodeHandle> nodeList`.

## Control Flow
Sender-side code builds `GetNodesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetNodesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetNodesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
