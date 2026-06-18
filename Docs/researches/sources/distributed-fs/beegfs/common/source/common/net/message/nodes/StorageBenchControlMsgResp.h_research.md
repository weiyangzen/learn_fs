# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsgResp.h

## Purpose
Defines `StorageBenchControlMsgResp`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_StorageBenchControlMsgResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`StorageBenchControlMsgResp` derives from `public NetMessageSerdes<StorageBenchControlMsgResp>` and uses `BaseType(NETMSGTYPE_StorageBenchControlMsgResp)` or an equivalent base constructor. Constructors include `StorageBenchControlMsgResp(StorageBenchStatus status, StorageBenchAction action, StorageBenchType type, int errorCode, StorageBenchResultsMap& results) : BaseType(NETMSGTYPE_StorageBenchControlMsgResp)`; `StorageBenchControlMsgResp() : BaseType(NETMSGTYPE_StorageBenchControlMsgResp)`. Serialization writes `status`, `action`, `type`, `errorCode`, `resultTargetIDs`, `resultValues`. Notable accessors/helpers include `getStatus()`, `getAction()`, `getType()`, `getErrorCode()`. Declared payload/backing members include `int32_t status`, `int32_t action`, `int32_t type`, `int32_t errorCode`, `UInt16List resultTargetIDs`, `Int64List resultValues`.

## Control Flow
Sender-side code builds `StorageBenchControlMsgResp` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/benchmark/StorageBench.h`, `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`, `common/toolkit/ZipIterator.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_StorageBenchControlMsgResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StorageBenchControlMsgResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
