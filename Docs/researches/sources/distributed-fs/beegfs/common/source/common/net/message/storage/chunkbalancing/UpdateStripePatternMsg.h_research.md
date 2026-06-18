# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/UpdateStripePatternMsg.h

## Purpose
Defines `UpdateStripePatternMsg`, a BeeGFS chunk balancing command message using `NETMSGTYPE_UpdateStripePattern`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UpdateStripePatternMsg` derives from `public MirroredMessageBase<UpdateStripePatternMsg>` and uses `BaseType(NETMSGTYPE_UpdateStripePattern)` or an equivalent base constructor. Constructors include `UpdateStripePatternMsg(uint16_t targetID, uint16_t destinationID, EntryInfo* entryInfo,std::string* relativePath, FhgfsOpsErr resyncRes, FileEvent* fileEvent) : BaseType(NETMSGTYPE_UpdateStripePattern)`; `UpdateStripePatternMsg() : BaseType(NETMSGTYPE_UpdateStripePattern)`. Serialization writes `targetID`, `destinationID`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `backedPtr(obj->relativePath, obj->parsed.relativePath)`, `resyncRes`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getTargetID()`, `getDestinationID()`, `getRelativePath()`, `getEntryInfo()`, `getFileEvent()`, `getResyncResult()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `uint16_t targetID`, `uint16_t destinationID`, `FileEvent fileEvent`, `std::string* relativePath`, `EntryInfo* entryInfoPtr`, `std::string relativePath`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `UpdateStripePatternMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/toolkit/serialization/Serialization.h`, `common/storage/FileEvent.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_UpdateStripePattern`. Feature flags: `UPDATESTRIPEPATTERNMSG_FLAG_HAS_EVENT`=1. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateStripePattern`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
