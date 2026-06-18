# sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncFileMsg.h

## Purpose
Defines `TruncFileMsg`, a BeeGFS storage target operation command message using `NETMSGTYPE_TruncFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`TruncFileMsg` derives from `public MirroredMessageBase<TruncFileMsg>` and uses `BaseType(NETMSGTYPE_TruncFile)` or an equivalent base constructor. Constructors include `TruncFileMsg(int64_t filesize, EntryInfo* entryInfo) : BaseType(NETMSGTYPE_TruncFile)`; `TruncFileMsg() : BaseType(NETMSGTYPE_TruncFile)`. Serialization writes `filesize`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `dynAttribs`, `mirroredTimestamps`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getFilesize()`, `getEntryInfo()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `int64_t filesize`, `FileEvent fileEvent`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `DynamicFileAttribsVec dynAttribs`, `MirroredTimestamps mirroredTimestamps`.

## Control Flow
Sender-side code builds `TruncFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_TruncFile`. Feature flags: `TRUNCFILEMSG_FLAG_USE_QUOTA`=1, `TRUNCFILEMSG_FLAG_HAS_EVENT`=2. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_TruncFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
