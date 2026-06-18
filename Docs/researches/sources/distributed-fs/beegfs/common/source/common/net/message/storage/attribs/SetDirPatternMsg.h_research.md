# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetDirPatternMsg.h

## Purpose
Defines `SetDirPatternMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetDirPattern`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetDirPatternMsg` derives from `public MirroredMessageBase<SetDirPatternMsg>` and uses `BaseType(NETMSGTYPE_SetDirPattern)` or an equivalent base constructor. Constructors include `SetDirPatternMsg(EntryInfo* entryInfo, StripePattern* pattern, RemoteStorageTarget* rst) : BaseType(NETMSGTYPE_SetDirPattern)`; `SetDirPatternMsg() : BaseType(NETMSGTYPE_SetDirPattern)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `backedPtr(obj->rstPtr, obj->rst)`, `uid`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `getPattern()`, `getEntryInfo()`, `getRemoteStorageTarget()`, `getUID()`, `setUID()`, `setMsgHeaderFeatureFlags()`, `supportsMirroring()`. Declared payload/backing members include `static const uint32_t HAS_UID`, `uint32_t uid`, `EntryInfo* entryInfoPtr`, `StripePattern* pattern`, `RemoteStorageTarget* rstPtr`, `EntryInfo entryInfo`, `RemoteStorageTarget rst`, `std::unique_ptr<StripePattern> pattern`.

## Control Flow
Sender-side code builds `SetDirPatternMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/StripePattern.h`, `common/storage/EntryInfo.h`, `common/storage/RemoteStorageTarget.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetDirPattern`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetDirPattern`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
