# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetAttrMsg.h

## Purpose
Defines `SetAttrMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetAttr`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetAttrMsg` derives from `public MirroredMessageBase<SetAttrMsg>` and uses `BaseType(NETMSGTYPE_SetAttr)` or an equivalent base constructor. Constructors include `SetAttrMsg(EntryInfo *entryInfo, int validAttribs, SettableFileAttribs* attribs) : BaseType(NETMSGTYPE_SetAttr), validAttribs(validAttribs), attribs(*attribs), entryInfoPtr(entryInfo)`; `SetAttrMsg() : BaseType(NETMSGTYPE_SetAttr)`. Serialization writes `validAttribs`, `attribs`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `inodeTimestamps`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getValidAttribs()`, `getAttribs()`, `getEntryInfo()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`, `supportsMirroring()`. Declared payload/backing members include `int32_t validAttribs`, `SettableFileAttribs attribs`, `FileEvent fileEvent`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `MirroredTimestamps inodeTimestamps`.

## Control Flow
Sender-side code builds `SetAttrMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`, `common/storage/StorageDefinitions.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetAttr`. Feature flags: `SETATTRMSG_FLAG_USE_QUOTA`=1, `SETATTRMSG_FLAG_HAS_EVENT`=4, `SETATTRMSG_FLAG_INCR_NLINKCNT`=8, `SETATTRMSG_FLAG_DECR_NLINKCNT`=16. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetAttr`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
