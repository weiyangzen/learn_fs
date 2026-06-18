# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MoveFileInodeRespMsg.h

## Purpose
Defines `MoveFileInodeRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MoveFileInodeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MoveFileInodeRespMsg` derives from `public NetMessageSerdes<MoveFileInodeRespMsg>` and uses `BaseType(NETMSGTYPE_MoveFileInodeResp)` or an equivalent base constructor. Constructors include `MoveFileInodeRespMsg(FhgfsOpsErr result, unsigned linkCount) : BaseType(NETMSGTYPE_MoveFileInodeResp)`; `MoveFileInodeRespMsg() : BaseType(NETMSGTYPE_MoveFileInodeResp)`. Serialization writes `result`, `linkCount`. Notable accessors/helpers include `getResult()`, `getHardlinkCount()`. Declared payload/backing members include `FhgfsOpsErr result`, `unsigned linkCount`.

## Control Flow
Sender-side code builds `MoveFileInodeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MoveFileInodeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MoveFileInodeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
