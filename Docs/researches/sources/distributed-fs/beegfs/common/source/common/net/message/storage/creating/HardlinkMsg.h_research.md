# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/HardlinkMsg.h

## Purpose
Defines `HardlinkMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_Hardlink`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`HardlinkMsg` derives from `public MirroredMessageBase<HardlinkMsg>` and uses `BaseType(NETMSGTYPE_Hardlink)` or an equivalent base constructor. Constructors include `HardlinkMsg(EntryInfo* fromDirInfo, std::string& fromName, EntryInfo* fromInfo, EntryInfo* toDirInfo, std::string& toName) : BaseType(NETMSGTYPE_Hardlink)`; `HardlinkMsg() : BaseType(NETMSGTYPE_Hardlink)`. Serialization writes `backedPtr(obj->fromInfoPtr, obj->fromInfo)`, `backedPtr(obj->toDirInfoPtr, obj->toDirInfo)`, `stringAlign4(obj->toName)`, `fromDirInfoPtr`, `backedPtr(obj->fromDirInfoPtr, obj->fromDirInfo)`, `stringAlign4(obj->fromName)`, `fileEvent`, `dirTimestamps`, `fileTimestamps`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getFromInfo()`, `getFromDirInfo()`, `getToDirInfo()`, `getFromName()`, `getToName()`, `supportsMirroring()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `std::string fromName`, `std::string toName`, `FileEvent fileEvent`, `EntryInfo* fromInfoPtr`, `EntryInfo* fromDirInfoPtr`, `EntryInfo* toDirInfoPtr`, `EntryInfo fromInfo`, `EntryInfo fromDirInfo`, `EntryInfo toDirInfo`, `MirroredTimestamps dirTimestamps`, `MirroredTimestamps fileTimestamps`.

## Control Flow
Sender-side code builds `HardlinkMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_Hardlink`. Feature flags: `HARDLINKMSG_FLAG_IS_TO_DENTRY_CREATE`=1, `HARDLINKMSG_FLAG_HAS_EVENT`=2. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_Hardlink`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
