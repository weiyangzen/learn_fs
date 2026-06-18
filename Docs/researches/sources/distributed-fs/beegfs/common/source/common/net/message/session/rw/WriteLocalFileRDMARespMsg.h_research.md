# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRDMARespMsg.h

## Purpose
Defines `WriteLocalFileRDMARespMsg`, the response payload wrapper for BeeGFS storage I/O session RPCs using `NETMSGTYPE_WriteLocalFileRDMAResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`WriteLocalFileRDMARespMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_WriteLocalFileRDMAResp)` or an equivalent base constructor. Constructors include `WriteLocalFileRDMARespMsg(int64_t result) : SimpleInt64Msg(NETMSGTYPE_WriteLocalFileRDMAResp, result)`; `WriteLocalFileRDMARespMsg() : SimpleInt64Msg(NETMSGTYPE_WriteLocalFileRDMAResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `WriteLocalFileRDMARespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_WriteLocalFileRDMAResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
I/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_WriteLocalFileRDMAResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Validate control-message fields together with data-transfer or RDMA descriptor handling.
