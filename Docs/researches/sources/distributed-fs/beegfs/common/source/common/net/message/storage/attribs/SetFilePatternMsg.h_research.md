# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFilePatternMsg.h

## Purpose
Defines `SetFilePatternMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetFilePattern`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetFilePatternMsg` derives from `public MirroredMessageBase<SetFilePatternMsg>` and uses `BaseType(NETMSGTYPE_SetFilePattern)` or an equivalent base constructor. Constructors include `SetFilePatternMsg(EntryInfo* entryInfo, RemoteStorageTarget* rst) : BaseType(NETMSGTYPE_SetFilePattern)`; `SetFilePatternMsg() : BaseType(NETMSGTYPE_SetFilePattern)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `backedPtr(obj->rstPtr, obj->rst)`. Notable accessors/helpers include `getEntryInfo()`, `getRemoteStorageTarget()`, `supportsMirroring()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `RemoteStorageTarget* rstPtr`, `EntryInfo entryInfo`, `RemoteStorageTarget rst`.

## Control Flow
Sender-side code builds `SetFilePatternMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/RemoteStorageTarget.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetFilePattern`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetFilePattern`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
