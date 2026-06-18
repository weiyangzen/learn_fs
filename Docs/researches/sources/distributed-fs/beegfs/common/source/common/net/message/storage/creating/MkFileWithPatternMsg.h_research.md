# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileWithPatternMsg.h

## Purpose
Defines `MkFileWithPatternMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_MkFileWithPattern`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`MkFileWithPatternMsg` derives from `public MirroredMessageBase<MkFileWithPatternMsg>` and uses `BaseType(NETMSGTYPE_MkFileWithPattern)` or an equivalent base constructor. Constructors include `MkFileWithPatternMsg(const EntryInfo* parentInfo, const std::string& newFileName, const unsigned userID, const unsigned groupID, const int mode, const int umask, StripePattern* pattern, RemoteStorageTarget* rst) : BaseType(NETMSGTYPE_MkFileWithPattern), newFileName(newFileName.c_str()), newFileNameLen(newFileName.length()), userID(userID), groupID(groupID), mode(mode), umask(umask), parentInfoPtr(parentInfo), pattern(pattern), rstPtr(rst)`; `MkFileWithPatternMsg() : BaseType(NETMSGTYPE_MkFileWithPattern)`. Serialization writes `userID`, `groupID`, `mode`, `umask`, `backedPtr(obj->parentInfoPtr, obj->parentInfo)`, `rawString(obj->newFileName, obj->newFileNameLen, 4)`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `backedPtr(obj->rstPtr, obj->rst)`. Notable accessors/helpers include `getPattern()`, `getRemoteStorageTarget()`, `getUserID()`, `getGroupID()`, `getMode()`, `getUmask()`, `getParentInfo()`, `getNewFileName()`. Declared payload/backing members include `const char* newFileName`, `unsigned newFileNameLen`, `uint32_t userID`, `uint32_t groupID`, `int32_t mode`, `int32_t umask`, `const EntryInfo* parentInfoPtr`, `StripePattern* pattern`, `RemoteStorageTarget* rstPtr`, `EntryInfo parentInfo`, `RemoteStorageTarget rst`, `std::unique_ptr<StripePattern> pattern`.

## Control Flow
Sender-side code builds `MkFileWithPatternMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/StripePattern.h`, `common/storage/RemoteStorageTarget.h`, `common/storage/EntryInfo.h`, `common/storage/Path.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkFileWithPattern`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkFileWithPattern`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
