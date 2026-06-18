# sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileMsg.h

## Purpose
Defines `TruncLocalFileMsg`, a BeeGFS storage target operation command message using `NETMSGTYPE_TruncLocalFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`TruncLocalFileMsg` derives from `public NetMessageSerdes<TruncLocalFileMsg>` and uses `BaseType(NETMSGTYPE_TruncLocalFile)` or an equivalent base constructor. Constructors include `TruncLocalFileMsg(int64_t filesize, std::string& entryID, uint16_t targetID, PathInfo* pathInfo) : BaseType(NETMSGTYPE_TruncLocalFile)`; `TruncLocalFileMsg() : BaseType(NETMSGTYPE_TruncLocalFile)`. Serialization writes `filesize`, `userID`, `groupID`, `rawString(obj->entryID, obj->entryIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `getFilesize()`, `getEntryID()`, `getTargetID()`, `getPathInfo()`, `getUserID()`, `getGroupID()`, `setUserdataForQuota()`. Declared payload/backing members include `int64_t filesize`, `unsigned entryIDLen`, `const char* entryID`, `uint16_t targetID`, `uint32_t userID`, `uint32_t groupID`, `PathInfo* pathInfoPtr`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `TruncLocalFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/PathInfo.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_TruncLocalFile`. Feature flags: `TRUNCLOCALFILEMSG_FLAG_NODYNAMICATTRIBS`=1, `TRUNCLOCALFILEMSG_FLAG_USE_QUOTA`=2, `TRUNCLOCALFILEMSG_FLAG_BUDDYMIRROR`=4, `TRUNCLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_TruncLocalFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
