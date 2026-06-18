# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkLocalDirMsg.h

## Purpose
Defines `MkLocalDirMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_MkLocalDir`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`MkLocalDirMsg` derives from `public MirroredMessageBase<MkLocalDirMsg>` and uses `BaseType(NETMSGTYPE_MkLocalDir)` or an equivalent base constructor. Constructors include `MkLocalDirMsg(EntryInfo* entryInfo, unsigned userID, unsigned groupID, int mode, StripePattern* pattern, RemoteStorageTarget* rst, NumNodeID parentNodeID, const CharVector& defaultACLXAttr, const CharVector& accessACLXAttr) : BaseType(NETMSGTYPE_MkLocalDir), defaultACLXAttr(defaultACLXAttr), accessACLXAttr(accessACLXAttr)`; `MkLocalDirMsg() : BaseType(NETMSGTYPE_MkLocalDir)`. Serialization writes `userID`, `groupID`, `mode`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `backedPtr(obj->rstPtr, obj->rst)`, `parentNodeID`, `defaultACLXAttr`, `accessACLXAttr`, `dirTimestamps`. Notable accessors/helpers include `supportsMirroring()`, `getPattern()`, `setPattern()`, `getRemoteStorageTarget()`, `getUserID()`, `getGroupID()`, `getMode()`, `getParentNodeID()`, `getEntryInfo()`, `getDefaultACLXAttr()`, `getAccessACLXAttr()`, `setDirTimestamps()`. Declared payload/backing members include `uint32_t userID`, `uint32_t groupID`, `int32_t mode`, `NumNodeID parentNodeID`, `EntryInfo* entryInfoPtr`, `StripePattern* pattern`, `RemoteStorageTarget* rstPtr`, `EntryInfo entryInfo`, `RemoteStorageTarget rst`, `std::unique_ptr<StripePattern> pattern`, `CharVector defaultACLXAttr`, `CharVector accessACLXAttr`, `MirroredTimestamps dirTimestamps`.

## Control Flow
Sender-side code builds `MkLocalDirMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/striping/StripePattern.h`, `common/storage/RemoteStorageTarget.h`, `common/storage/EntryInfo.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkLocalDir`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkLocalDir`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
