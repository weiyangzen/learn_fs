# sources/distributed-fs/beegfs/common/source/common/net/message/session/GetFileVersionMsg.h

## Purpose
Defines `GetFileVersionMsg`, a BeeGFS session lifecycle query/request message using `NETMSGTYPE_GetFileVersion`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetFileVersionMsg` derives from `public MirroredMessageBase<GetFileVersionMsg>` and uses `BaseType(NETMSGTYPE_GetFileVersion)` or an equivalent base constructor. Constructors include `GetFileVersionMsg(EntryInfo& entryInfo) : BaseType(NETMSGTYPE_GetFileVersion), entryInfo(&entryInfo)`; `GetFileVersionMsg() : BaseType(NETMSGTYPE_GetFileVersion)`. Serialization writes `backedPtr(obj->entryInfo, obj->parsed.entryInfo)`. Notable accessors/helpers include `supportsMirroring()`, `getEntryInfo()`. Declared payload/backing members include `EntryInfo* entryInfo`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `GetFileVersionMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_GetFileVersion`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetFileVersion`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps. Check empty result, boundary, and continuation cursor behavior.
