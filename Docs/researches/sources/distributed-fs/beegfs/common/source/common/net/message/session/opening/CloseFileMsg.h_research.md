# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseFileMsg.h

## Purpose
Defines `CloseFileMsg`, a BeeGFS file open and close session command message using `NETMSGTYPE_CloseFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`CloseFileMsg` derives from `public MirroredMessageBase<CloseFileMsg>` and uses `BaseType(NETMSGTYPE_CloseFile)` or an equivalent base constructor. Constructors include `CloseFileMsg(const NumNodeID clientNumID, const std::string& fileHandleID, EntryInfo* entryInfo, const int maxUsedNodeIndex) : BaseType(NETMSGTYPE_CloseFile)`; `CloseFileMsg() : BaseType(NETMSGTYPE_CloseFile)`. Serialization writes `clientNumID`, `stringAlign4(obj->fileHandleID)`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `maxUsedNodeIndex`, `dynAttribs`, `inodeTimestamps`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `supportsMirroring()`, `getClientNumID()`, `getFileHandleID()`, `getMaxUsedNodeIndex()`, `getEntryInfo()`, `getFileEvent()`. Declared payload/backing members include `NumNodeID clientNumID`, `std::string fileHandleID`, `int32_t maxUsedNodeIndex`, `FileEvent fileEvent`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `DynamicFileAttribsVec dynAttribs`, `MirroredTimestamps inodeTimestamps`.

## Control Flow
Sender-side code builds `CloseFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/StatData.h`, `common/storage/striping/DynamicFileAttribs.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_CloseFile`. Feature flags: `CLOSEFILEMSG_FLAG_EARLYRESPONSE`=1, `CLOSEFILEMSG_FLAG_CANCELAPPENDLOCKS`=2, `CLOSEFILEMSG_FLAG_DYNATTRIBS`=4, `CLOSEFILEMSG_FLAG_HAS_EVENT`=8. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CloseFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
