# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockRangeMsg.h

## Purpose
Defines `FLockRangeMsg`, a BeeGFS session locking command message using `NETMSGTYPE_FLockRange`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`FLockRangeMsg` derives from `public MirroredMessageBase<FLockRangeMsg>` and uses `BaseType(NETMSGTYPE_FLockRange)` or an equivalent base constructor. Constructors include `FLockRangeMsg(const NumNodeID clientNumID, const char* fileHandleID, const int ownerPID, const int lockTypeFlags, const int64_t start, const int64_t end, const char* lockAckID) : BaseType(NETMSGTYPE_FLockRange)`; `FLockRangeMsg() : BaseType(NETMSGTYPE_FLockRange)`. Serialization writes `clientNumID`, `start`, `end`, `ownerPID`, `lockTypeFlags`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `rawString(obj->lockAckID, obj->lockAckIDLen, 4)`. Notable accessors/helpers include `supportsMirroring()`, `getClientNumID()`, `getFileHandleID()`, `getOwnerPID()`, `getLockTypeFlags()`, `getStart()`, `getEnd()`, `getLockAckID()`, `getEntryInfo()`. Declared payload/backing members include `NumNodeID clientNumID`, `const char* fileHandleID`, `unsigned fileHandleIDLen`, `int32_t lockTypeFlags`, `uint64_t start`, `uint64_t end`, `const char* lockAckID`, `unsigned lockAckIDLen`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `FLockRangeMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_FLockRange`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FLockRange`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
