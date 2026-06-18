# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveDirEntriesRespMsg.h

## Purpose
Defines `RetrieveDirEntriesRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_RetrieveDirEntriesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RetrieveDirEntriesRespMsg` derives from `public NetMessageSerdes<RetrieveDirEntriesRespMsg>` and uses `BaseType(NETMSGTYPE_RetrieveDirEntriesResp)` or an equivalent base constructor. Constructors include `RetrieveDirEntriesRespMsg(FsckContDirList* fsckContDirs, FsckDirEntryList* fsckDirEntries, FsckFileInodeList* inlinedFileInodes, std::string& currentContDirID, int64_t newHashDirOffset, int64_t newContDirOffset) : BaseType(NETMSGTYPE_RetrieveDirEntriesResp)`; `RetrieveDirEntriesRespMsg() : BaseType(NETMSGTYPE_RetrieveDirEntriesResp)`. Serialization writes `rawString(obj->currentContDirID, obj->currentContDirIDLen, 4)`, `newHashDirOffset`, `newContDirOffset`, `backedPtr(obj->fsckContDirs, obj->parsed.fsckContDirs)`, `backedPtr(obj->fsckDirEntries, obj->parsed.fsckDirEntries)`, `backedPtr(obj->inlinedFileInodes, obj->parsed.inlinedFileInodes)`. Notable accessors/helpers include `getContDirs()`, `getDirEntries()`, `getInlinedFileInodes()`, `getNewHashDirOffset()`, `getNewContDirOffset()`, `getCurrentContDirID()`. Declared payload/backing members include `const char* currentContDirID`, `unsigned currentContDirIDLen`, `int64_t newHashDirOffset`, `int64_t newContDirOffset`, `FsckContDirList* fsckContDirs`, `FsckDirEntryList* fsckDirEntries`, `FsckFileInodeList* inlinedFileInodes`, `FsckContDirList fsckContDirs`, `FsckDirEntryList fsckDirEntries`, `FsckFileInodeList inlinedFileInodes`.

## Control Flow
Sender-side code builds `RetrieveDirEntriesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/fsck/FsckContDir.h`, `common/fsck/FsckDirEntry.h`, `common/fsck/FsckFileInode.h`, `common/net/message/NetMessage.h`, `common/toolkit/ListTk.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveDirEntriesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveDirEntriesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
