# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.h

## Purpose
Defines `ReadLocalFileRDMAMsg`, a BeeGFS storage I/O session command message using `NETMSGTYPE_ReadLocalFileRDMA`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ReadLocalFileRDMAMsg` derives from `public ReadLocalFileV2MsgBase, public NetMessageSerdes<ReadLocalFileRDMAMsg>` and uses `BaseType(NETMSGTYPE_ReadLocalFileRDMA)` or an equivalent base constructor. Constructors include `ReadLocalFileRDMAMsg(NumNodeID clientNumID, const char* fileHandleID, uint16_t targetID, PathInfo* pathInfoPtr, unsigned accessFlags, int64_t offset, int64_t count) : ReadLocalFileV2MsgBase(clientNumID, fileHandleID, targetID, pathInfoPtr, accessFlags, offset, count), BaseType(NETMSGTYPE_ReadLocalFileRDMA)`; `ReadLocalFileRDMAMsg() : ReadLocalFileV2MsgBase(), BaseType(NETMSGTYPE_ReadLocalFileRDMA)`. Serialization writes `rdmaInfo`. Notable accessors/helpers include `getRdmaInfo()`, `getSupportedHeaderFeatureFlagsMask()`, `isMsgValid()`, `isValid()`. Declared payload/backing members include `RdmaInfo rdmaInfo`.

## Control Flow
Sender-side code builds `ReadLocalFileRDMAMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`, `common/storage/RdmaInfo.h`, `common/app/log/LogContext.h`, `common/net/message/session/rw/ReadLocalFileV2Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_ReadLocalFileRDMA`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
I/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ReadLocalFileRDMA`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior. Validate control-message fields together with data-transfer or RDMA descriptor handling.
