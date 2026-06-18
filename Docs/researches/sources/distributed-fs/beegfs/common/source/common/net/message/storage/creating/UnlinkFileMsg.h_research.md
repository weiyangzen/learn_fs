# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkFileMsg.h

## Purpose
Defines `UnlinkFileMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_UnlinkFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UnlinkFileMsg` derives from `public MirroredMessageBase<UnlinkFileMsg>` and uses `BaseType(NETMSGTYPE_UnlinkFile)` or an equivalent base constructor. Constructors include `UnlinkFileMsg(EntryInfo* parentInfo, std::string& delFileName) : BaseType(NETMSGTYPE_UnlinkFile)`; `UnlinkFileMsg() : BaseType(NETMSGTYPE_UnlinkFile)`. Serialization writes `backedPtr(obj->parentInfoPtr, obj->parentInfo)`, `stringAlign4(obj->delFileName)`, `fileEvent`, `dirTimestamps`, `fileInfo`, `fileTimestamps`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getParentInfo()`, `getDelFileName()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `std::string delFileName`, `FileEvent fileEvent`, `EntryInfo* parentInfoPtr`, `EntryInfo parentInfo`, `MirroredTimestamps dirTimestamps`, `EntryInfo fileInfo`, `MirroredTimestamps fileTimestamps`.

## Control Flow
Sender-side code builds `UnlinkFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkFile`. Feature flags: `UNLINKFILEMSG_FLAG_HAS_EVENT`=1. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
