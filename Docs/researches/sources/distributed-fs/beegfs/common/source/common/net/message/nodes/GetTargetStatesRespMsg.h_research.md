# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetStatesRespMsg.h

## Purpose
Defines `GetTargetStatesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetTargetStatesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetTargetStatesRespMsg` derives from `public NetMessageSerdes<GetTargetStatesRespMsg>` and uses `BaseType(NETMSGTYPE_GetTargetStatesResp)` or an equivalent base constructor. Constructors include `GetTargetStatesRespMsg(UInt16List* targetIDs, UInt8List* reachabilityStates, UInt8List* consistencyStates) : BaseType(NETMSGTYPE_GetTargetStatesResp)`; `GetTargetStatesRespMsg() : BaseType(NETMSGTYPE_GetTargetStatesResp)`. Serialization writes `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`, `backedPtr(obj->reachabilityStates, obj->parsed.reachabilityStates)`, `backedPtr(obj->consistencyStates, obj->parsed.consistencyStates)`. Notable accessors/helpers include `getTargetIDs()`, `getReachabilityStates()`, `getConsistencyStates()`. Declared payload/backing members include `UInt16List* targetIDs`, `UInt8List* reachabilityStates`, `UInt8List* consistencyStates`, `UInt16List targetIDs`, `UInt8List reachabilityStates`, `UInt8List consistencyStates`.

## Control Flow
Sender-side code builds `GetTargetStatesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`, `common/nodes/TargetStateStore.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetStatesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetStatesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
