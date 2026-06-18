# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkLocalDirRespMsg.h

## Purpose
Defines `MkLocalDirRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MkLocalDirResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MkLocalDirRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_MkLocalDirResp)` or an equivalent base constructor. Constructors include `MkLocalDirRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_MkLocalDirResp, result)`; `MkLocalDirRespMsg() : SimpleIntMsg(NETMSGTYPE_MkLocalDirResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `MkLocalDirRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkLocalDirResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkLocalDirResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
