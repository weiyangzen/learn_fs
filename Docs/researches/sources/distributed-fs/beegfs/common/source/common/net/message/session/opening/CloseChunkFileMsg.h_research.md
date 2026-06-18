# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileMsg.h

## Purpose
Defines `CloseChunkFileMsg`, a BeeGFS file open and close session command message using `NETMSGTYPE_CloseChunkFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`CloseChunkFileMsg` derives from `public NetMessageSerdes<CloseChunkFileMsg>` and uses `BaseType(NETMSGTYPE_CloseChunkFile)` or an equivalent base constructor. Constructors include `CloseChunkFileMsg(const NumNodeID sessionID, const std::string& fileHandleID, const uint16_t targetID, const PathInfo* pathInfo) : BaseType(NETMSGTYPE_CloseChunkFile)`; `CloseChunkFileMsg() : BaseType(NETMSGTYPE_CloseChunkFile)`. Serialization writes `sessionID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getSessionID()`, `getFileHandleID()`, `getTargetID()`, `getPathInfo()`. Declared payload/backing members include `NumNodeID sessionID`, `unsigned fileHandleIDLen`, `const char* fileHandleID`, `uint16_t targetID`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `CloseChunkFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_CloseChunkFile`. Feature flags: `CLOSECHUNKFILEMSG_FLAG_NODYNAMICATTRIBS`=1, `CLOSECHUNKFILEMSG_FLAG_BUDDYMIRROR`=4, `CLOSECHUNKFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CloseChunkFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
