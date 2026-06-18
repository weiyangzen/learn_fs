# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeRespMsg.h

## Purpose
Defines `RegisterNodeRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_RegisterNodeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RegisterNodeRespMsg` derives from `public NetMessageSerdes<RegisterNodeRespMsg>` and uses `BaseType(NETMSGTYPE_RegisterNodeResp)` or an equivalent base constructor. Constructors include `RegisterNodeRespMsg(NumNodeID nodeNumID) : BaseType(NETMSGTYPE_RegisterNodeResp), nodeNumID(nodeNumID)`; `RegisterNodeRespMsg() : BaseType(NETMSGTYPE_RegisterNodeResp)`. Serialization writes `nodeNumID`, `grpcPort`, `fsUUID`. Notable accessors/helpers include `getNodeNumID()`. Declared payload/backing members include `NumNodeID nodeNumID`, `uint16_t grpcPort`, `std::string fsUUID`.

## Control Flow
Sender-side code builds `RegisterNodeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `stdint.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RegisterNodeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RegisterNodeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
