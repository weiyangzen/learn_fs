# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/OpenFileMsg.h

## Purpose
Defines `OpenFileMsg`, a BeeGFS file open and close session command message using `NETMSGTYPE_OpenFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`OpenFileMsg` derives from `public MirroredMessageBase<OpenFileMsg>` and uses `BaseType(NETMSGTYPE_OpenFile)` or an equivalent base constructor. Constructors include `OpenFileMsg(const NumNodeID clientNumID, const EntryInfo* entryInfo, const unsigned accessFlags) : BaseType(NETMSGTYPE_OpenFile), clientNumID(clientNumID), accessFlags(accessFlags), entryInfoPtr(entryInfo)`; `OpenFileMsg() : BaseType(NETMSGTYPE_OpenFile)`. Serialization writes `clientNumID`, `accessFlags`, `sessionFileID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `fileTimestamps`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getClientNumID()`, `getEntryInfo()`, `getAccessFlags()`, `getSupportedHeaderFeatureFlagsMask()`, `supportsMirroring()`, `getFileHandleID()`, `setFileHandleID()`, `getSessionFileID()`, `setSessionFileID()`, `getFileEvent()`. Declared payload/backing members include `NumNodeID clientNumID`, `uint32_t accessFlags`, `uint32_t sessionFileID`, `const char* fileHandleID`, `unsigned fileHandleIDLen`, `FileEvent fileEvent`, `const EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `MirroredTimestamps fileTimestamps`.

## Control Flow
Sender-side code builds `OpenFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_OpenFile`. Feature flags: `OPENFILEMSG_FLAG_USE_QUOTA`=1, `OPENFILEMSG_FLAG_HAS_EVENT`=2, `OPENFILEMSG_FLAG_BYPASS_ACCESS_CHECK`=4. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_OpenFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
