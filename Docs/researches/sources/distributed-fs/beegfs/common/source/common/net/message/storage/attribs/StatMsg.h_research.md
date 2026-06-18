# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/StatMsg.h

## Purpose
Defines `StatMsg`, a BeeGFS metadata and storage attributes query/request message using `NETMSGTYPE_Stat`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`StatMsg` derives from `public MirroredMessageBase<StatMsg>` and uses `BaseType(NETMSGTYPE_Stat)` or an equivalent base constructor. Constructors include `StatMsg(EntryInfo* entryInfo) : BaseType(NETMSGTYPE_Stat)`; `StatMsg() : BaseType(NETMSGTYPE_Stat)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `supportsMirroring()`, `getEntryInfo()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `StatMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/Path.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_Stat`. Feature flags: `STATMSG_FLAG_GET_PARENTINFO`=1. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_Stat`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
