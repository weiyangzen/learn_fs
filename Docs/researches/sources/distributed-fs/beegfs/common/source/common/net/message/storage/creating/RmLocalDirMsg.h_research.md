# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmLocalDirMsg.h

## Purpose
Defines `RmLocalDirMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_RmLocalDir`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RmLocalDirMsg` derives from `public MirroredMessageBase<RmLocalDirMsg>` and uses `BaseType(NETMSGTYPE_RmLocalDir)` or an equivalent base constructor. Constructors include `RmLocalDirMsg(EntryInfo* delEntryInfo) : BaseType(NETMSGTYPE_RmLocalDir)`; `RmLocalDirMsg() : BaseType(NETMSGTYPE_RmLocalDir)`. Serialization writes `backedPtr(obj->delEntryInfoPtr, obj->delEntryInfo)`. Notable accessors/helpers include `getDelEntryInfo()`, `supportsMirroring()`. Declared payload/backing members include `EntryInfo* delEntryInfoPtr`, `EntryInfo delEntryInfo`.

## Control Flow
Sender-side code builds `RmLocalDirMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmLocalDir`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmLocalDir`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
