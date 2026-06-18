# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogRespMsg.h

## Purpose
Defines `LogRespMsg`, the response payload wrapper for BeeGFS helper daemon RPCs using `NETMSGTYPE_LogResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`LogRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_LogResp)` or an equivalent base constructor. Constructors include `LogRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_LogResp, result)`; `LogRespMsg() : SimpleIntMsg(NETMSGTYPE_LogResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `LogRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_LogResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_LogResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
