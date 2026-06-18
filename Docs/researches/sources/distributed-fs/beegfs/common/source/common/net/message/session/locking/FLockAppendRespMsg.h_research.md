# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockAppendRespMsg.h

## Purpose
Defines `FLockAppendRespMsg`, the response payload wrapper for BeeGFS session locking RPCs using `NETMSGTYPE_FLockAppendResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`FLockAppendRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_FLockAppendResp)` or an equivalent base constructor. Constructors include `FLockAppendRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_FLockAppendResp, result)`; `FLockAppendRespMsg() : SimpleIntMsg(NETMSGTYPE_FLockAppendResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `FLockAppendRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_FLockAppendResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FLockAppendResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
