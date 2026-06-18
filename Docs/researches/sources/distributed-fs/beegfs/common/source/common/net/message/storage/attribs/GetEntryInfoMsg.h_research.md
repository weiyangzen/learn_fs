# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetEntryInfoMsg.h

## Purpose
Defines `GetEntryInfoMsg`, a BeeGFS metadata and storage attributes query/request message using `NETMSGTYPE_GetEntryInfo`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetEntryInfoMsg` derives from `public MirroredMessageBase<GetEntryInfoMsg>` and uses `BaseType(NETMSGTYPE_GetEntryInfo)` or an equivalent base constructor. Constructors include `GetEntryInfoMsg(EntryInfo* entryInfo) : BaseType(NETMSGTYPE_GetEntryInfo)`; `GetEntryInfoMsg() : BaseType(NETMSGTYPE_GetEntryInfo)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`. Notable accessors/helpers include `getEntryInfo()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `GetEntryInfoMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetEntryInfo`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetEntryInfo`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps. Check empty result, boundary, and continuation cursor behavior.
