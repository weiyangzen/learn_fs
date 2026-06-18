# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileInodeRespMsg.h

## Purpose
Defines `UnlinkLocalFileInodeRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_UnlinkLocalFileInodeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UnlinkLocalFileInodeRespMsg` derives from `public NetMessageSerdes<UnlinkLocalFileInodeRespMsg>` and uses `BaseType(NETMSGTYPE_UnlinkLocalFileInodeResp)` or an equivalent base constructor. Constructors include `UnlinkLocalFileInodeRespMsg(FhgfsOpsErr result, unsigned linkCount) : BaseType(NETMSGTYPE_UnlinkLocalFileInodeResp)`; `UnlinkLocalFileInodeRespMsg() : BaseType(NETMSGTYPE_UnlinkLocalFileInodeResp)`. Serialization writes `result`, `preUnlinkHardlinkCount`. Notable accessors/helpers include `getResult()`, `getPreUnlinkHardlinkCount()`. Declared payload/backing members include `FhgfsOpsErr result`, `unsigned preUnlinkHardlinkCount`.

## Control Flow
Sender-side code builds `UnlinkLocalFileInodeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkLocalFileInodeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkLocalFileInodeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
