# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetConsistencyStatesRespMsg.h

## Purpose
Defines `GetTargetConsistencyStatesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetTargetConsistencyStatesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetTargetConsistencyStatesRespMsg` derives from `public NetMessageSerdes<GetTargetConsistencyStatesRespMsg>` and uses `BaseType(NETMSGTYPE_GetTargetConsistencyStatesResp)` or an equivalent base constructor. Constructors include `GetTargetConsistencyStatesRespMsg(const TargetConsistencyStateVec& states) : BaseType(NETMSGTYPE_GetTargetConsistencyStatesResp), states(states)`; `GetTargetConsistencyStatesRespMsg() : BaseType(NETMSGTYPE_GetTargetConsistencyStatesResp)`. Serialization writes `states`. Notable accessors/helpers include `getStates()`. Declared payload/backing members include `TargetConsistencyStateVec states`.

## Control Flow
Sender-side code builds `GetTargetConsistencyStatesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Depends primarily on the BeeGFS `NetMessage` serialization framework. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetConsistencyStatesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetConsistencyStatesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
