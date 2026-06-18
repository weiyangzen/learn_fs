# sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileRespMsg.h

## Purpose
Defines `FSyncLocalFileRespMsg`, the response payload wrapper for BeeGFS session lifecycle RPCs using `NETMSGTYPE_FSyncLocalFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`FSyncLocalFileRespMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_FSyncLocalFileResp)` or an equivalent base constructor. Constructors include `FSyncLocalFileRespMsg(int64_t result) : SimpleInt64Msg(NETMSGTYPE_FSyncLocalFileResp, result)`; `FSyncLocalFileRespMsg() : SimpleInt64Msg(NETMSGTYPE_FSyncLocalFileResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `FSyncLocalFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `../SimpleInt64Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_FSyncLocalFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FSyncLocalFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
