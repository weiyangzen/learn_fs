# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileV2Msg.h

## Purpose
Defines `ReadLocalFileV2Msg`, a BeeGFS storage I/O session command message using `NETMSGTYPE_ReadLocalFileV2`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ReadLocalFileV2Msg` derives from `public ReadLocalFileV2MsgBase, public NetMessageSerdes<ReadLocalFileV2Msg>` and uses `BaseType(NETMSGTYPE_ReadLocalFileV2)` or an equivalent base constructor. Constructors include `ReadLocalFileV2Msg(NumNodeID clientNumID, const char* fileHandleID, uint16_t targetID, PathInfo* pathInfoPtr, unsigned accessFlags, int64_t offset, int64_t count) : ReadLocalFileV2MsgBase(clientNumID, fileHandleID, targetID, pathInfoPtr, accessFlags, offset, count), BaseType(NETMSGTYPE_ReadLocalFileV2)`; `ReadLocalFileV2Msg() : ReadLocalFileV2MsgBase(), BaseType(NETMSGTYPE_ReadLocalFileV2)`. Serialization writes `offset`, `count`, `accessFlags`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `clientNumID`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `ReadLocalFileV2Msg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_ReadLocalFileV2`. Feature flags: `READLOCALFILEMSG_FLAG_SESSION_CHECK`=1, `READLOCALFILEMSG_FLAG_DISABLE_IO`=2, `READLOCALFILEMSG_FLAG_BUDDYMIRROR`=4, `READLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; offset cursors can repeat or skip records if callers mishandle continuation; i/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ReadLocalFileV2`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior. Validate control-message fields together with data-transfer or RDMA descriptor handling.
