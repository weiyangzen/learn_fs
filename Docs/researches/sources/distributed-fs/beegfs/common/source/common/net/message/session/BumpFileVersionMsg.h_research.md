# sources/distributed-fs/beegfs/common/source/common/net/message/session/BumpFileVersionMsg.h

## Purpose
Defines `BumpFileVersionMsg`, a BeeGFS session lifecycle command message using `NETMSGTYPE_BumpFileVersion`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`BumpFileVersionMsg` derives from `public MirroredMessageBase<BumpFileVersionMsg>` and uses `BaseType(NETMSGTYPE_BumpFileVersion)` or an equivalent base constructor. Constructors include `BumpFileVersionMsg(EntryInfo& entryInfo) : BaseType(NETMSGTYPE_BumpFileVersion), entryInfo(&entryInfo)`; `BumpFileVersionMsg() : BaseType(NETMSGTYPE_BumpFileVersion)`. Serialization writes `backedPtr(obj->entryInfo, obj->parsed.entryInfo)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getSupportedHeaderFeatureFlagsMask()`, `getEntryInfo()`, `getFileEvent()`. Declared payload/backing members include `EntryInfo* entryInfo`, `FileEvent fileEvent`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `BumpFileVersionMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_BumpFileVersion`. Feature flags: `BUMPFILEVERSIONMSG_FLAG_PERSISTENT`=1, `BUMPFILEVERSIONMSG_FLAG_HASEVENT`=2. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_BumpFileVersion`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
