# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileMsg.h

## Purpose
Defines `WriteLocalFileMsg`, a BeeGFS storage I/O session command message using `NETMSGTYPE_WriteLocalFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`WriteLocalFileMsg` derives from `public WriteLocalFileMsgBase, public NetMessageSerdes<WriteLocalFileMsg>` and uses `BaseType(NETMSGTYPE_WriteLocalFile)` or an equivalent base constructor. Constructors include `WriteLocalFileMsg(const NumNodeID clientNumID, const char* fileHandleID, const uint16_t targetID, const PathInfo* pathInfo, const unsigned accessFlags, const int64_t offset, const int64_t count) : WriteLocalFileMsgBase(clientNumID, fileHandleID, targetID, pathInfo, accessFlags, offset, count), BaseType(NETMSGTYPE_WriteLocalFile)`; `WriteLocalFileMsg() : WriteLocalFileMsgBase(), BaseType(NETMSGTYPE_WriteLocalFile)`. Serialization writes `offset`, `count`, `accessFlags`, `userID`, `groupID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `clientNumID`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `setUserdataForQuota()`, `getSupportedHeaderFeatureFlagsMask()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `WriteLocalFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_WriteLocalFile`. Feature flags: `WRITELOCALFILEMSG_FLAG_SESSION_CHECK`=1, `WRITELOCALFILEMSG_FLAG_USE_QUOTA`=2, `WRITELOCALFILEMSG_FLAG_DISABLE_IO`=4, `WRITELOCALFILEMSG_FLAG_BUDDYMIRROR`=8, `WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=16, `WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_FORWARD`=32.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; offset cursors can repeat or skip records if callers mishandle continuation; i/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_WriteLocalFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior. Validate control-message fields together with data-transfer or RDMA descriptor handling.
