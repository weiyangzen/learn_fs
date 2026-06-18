# subset-b-000545 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateDentriesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateDentriesRespMsg.h

## Purpose
Defines `RecreateDentriesRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_RecreateDentriesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RecreateDentriesRespMsg` derives from `public NetMessageSerdes<RecreateDentriesRespMsg>` and uses `BaseType(NETMSGTYPE_RecreateDentriesResp)` or an equivalent base constructor. Constructors include `RecreateDentriesRespMsg(FsckFsIDList* failedCreates, FsckDirEntryList* createdDentries, FsckFileInodeList* createdInodes) : BaseType(NETMSGTYPE_RecreateDentriesResp)`; `RecreateDentriesRespMsg() : BaseType(NETMSGTYPE_RecreateDentriesResp)`. Serialization writes `backedPtr(obj->failedCreates, obj->parsed.failedCreates)`, `backedPtr(obj->createdDentries, obj->parsed.createdDentries)`, `backedPtr(obj->createdInodes, obj->parsed.createdInodes)`. Notable accessors/helpers include `getFailedCreates()`, `getCreatedDentries()`, `getCreatedInodes()`. Declared payload/backing members include `FsckFsIDList* failedCreates`, `FsckDirEntryList* createdDentries`, `FsckFileInodeList* createdInodes`, `FsckFsIDList failedCreates`, `FsckDirEntryList createdDentries`, `FsckFileInodeList createdInodes`.

## Control Flow
Sender-side code builds `RecreateDentriesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckDirEntry.h`, `common/fsck/FsckFileInode.h`, `common/fsck/FsckFsID.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RecreateDentriesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RecreateDentriesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateDentriesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateFsIDsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateFsIDsMsg.h

## Purpose
Defines `RecreateFsIDsMsg`, a BeeGFS fsck repair and audit command message using `NETMSGTYPE_RecreateFsIDs`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RecreateFsIDsMsg` derives from `public NetMessageSerdes<RecreateFsIDsMsg>` and uses `BaseType(NETMSGTYPE_RecreateFsIDs)` or an equivalent base constructor. Constructors include `RecreateFsIDsMsg(FsckDirEntryList* entries) : BaseType(NETMSGTYPE_RecreateFsIDs)`; `RecreateFsIDsMsg() : BaseType(NETMSGTYPE_RecreateFsIDs)`. Serialization writes `backedPtr(obj->entries, obj->parsed.entries)`. Notable accessors/helpers include `getEntries()`. Declared payload/backing members include `FsckDirEntryList* entries`, `FsckDirEntryList entries`.

## Control Flow
Sender-side code builds `RecreateFsIDsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckDirEntry.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RecreateFsIDs`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RecreateFsIDs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateFsIDsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateFsIDsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateFsIDsRespMsg.h

## Purpose
Defines `RecreateFsIDsRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_RecreateFsIDsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RecreateFsIDsRespMsg` derives from `public NetMessageSerdes<RecreateFsIDsRespMsg>` and uses `BaseType(NETMSGTYPE_RecreateFsIDsResp)` or an equivalent base constructor. Constructors include `RecreateFsIDsRespMsg(FsckDirEntryList* failedEntries) : BaseType(NETMSGTYPE_RecreateFsIDsResp)`; `RecreateFsIDsRespMsg() : BaseType(NETMSGTYPE_RecreateFsIDsResp)`. Serialization writes `backedPtr(obj->failedEntries, obj->parsed.failedEntries)`. Notable accessors/helpers include `getFailedEntries()`. Declared payload/backing members include `FsckDirEntryList* failedEntries`, `FsckDirEntryList failedEntries`.

## Control Flow
Sender-side code builds `RecreateFsIDsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckDirEntry.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RecreateFsIDsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RecreateFsIDsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateFsIDsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RemoveInodesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RemoveInodesMsg.h

## Purpose
Defines `RemoveInodesMsg`, a BeeGFS fsck repair and audit command message using `NETMSGTYPE_RemoveInodes`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveInodesMsg` derives from `public NetMessageSerdes<RemoveInodesMsg>` and uses `BaseType(NETMSGTYPE_RemoveInodes)` or an equivalent base constructor. Constructors include `RemoveInodesMsg(std::vector<Item> items): BaseType(NETMSGTYPE_RemoveInodes), items(std::move(items))`; `RemoveInodesMsg() : BaseType(NETMSGTYPE_RemoveInodes)`. Serialization writes `items`. Declared payload/backing members include `std::vector<Item> items`.

## Control Flow
Sender-side code builds `RemoveInodesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageDefinitions.h`, `common/toolkit/ListTk.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RemoveInodes`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveInodes`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RemoveInodesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RemoveInodesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RemoveInodesRespMsg.h

## Purpose
Defines `RemoveInodesRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_RemoveInodesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RemoveInodesRespMsg` derives from `public NetMessageSerdes<RemoveInodesRespMsg>` and uses `BaseType(NETMSGTYPE_RemoveInodesResp)` or an equivalent base constructor. Constructors include `RemoveInodesRespMsg(StringList failedEntryIDList) : BaseType(NETMSGTYPE_RemoveInodesResp), failedEntryIDList(std::move(failedEntryIDList))`; `RemoveInodesRespMsg() : BaseType(NETMSGTYPE_RemoveInodesResp)`. Serialization writes `failedEntryIDList`. Declared payload/backing members include `StringList failedEntryIDList`.

## Control Flow
Sender-side code builds `RemoveInodesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageDefinitions.h`, `common/toolkit/ListTk.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RemoveInodesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveInodesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RemoveInodesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveDirEntriesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveDirEntriesMsg.h

## Purpose
Defines `RetrieveDirEntriesMsg`, a BeeGFS fsck repair and audit query/request message using `NETMSGTYPE_RetrieveDirEntries`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RetrieveDirEntriesMsg` derives from `public NetMessageSerdes<RetrieveDirEntriesMsg>` and uses `BaseType(NETMSGTYPE_RetrieveDirEntries)` or an equivalent base constructor. Constructors include `RetrieveDirEntriesMsg(unsigned hashDirNum, std::string& currentContDirID, unsigned maxOutEntries, int64_t lastHashDirOffset, int64_t lastContDirOffset, bool isBuddyMirrored) : BaseType(NETMSGTYPE_RetrieveDirEntries)`; `RetrieveDirEntriesMsg() : BaseType(NETMSGTYPE_RetrieveDirEntries)`. Serialization writes `hashDirNum`, `rawString(obj->currentContDirID, obj->currentContDirIDLen)`, `maxOutEntries`, `lastHashDirOffset`, `lastContDirOffset`, `isBuddyMirrored`. Notable accessors/helpers include `getCurrentContDirID()`, `getHashDirNum()`, `getLastContDirOffset()`, `getLastHashDirOffset()`, `getMaxOutEntries()`, `getIsBuddyMirrored()`. Declared payload/backing members include `uint32_t hashDirNum`, `unsigned currentContDirIDLen`, `uint32_t maxOutEntries`, `int64_t lastHashDirOffset`, `int64_t lastContDirOffset`, `bool isBuddyMirrored`.

## Control Flow
Sender-side code builds `RetrieveDirEntriesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/Path.h`, `common/storage/StorageDefinitions.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveDirEntries`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveDirEntries`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveDirEntriesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveDirEntriesRespMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveDirEntriesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveFsIDsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveFsIDsMsg.h

## Purpose
Defines `RetrieveFsIDsMsg`, a BeeGFS fsck repair and audit query/request message using `NETMSGTYPE_RetrieveFsIDs`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RetrieveFsIDsMsg` derives from `public NetMessageSerdes<RetrieveFsIDsMsg>` and uses `BaseType(NETMSGTYPE_RetrieveFsIDs)` or an equivalent base constructor. Constructors include `RetrieveFsIDsMsg(unsigned hashDirNum, bool buddyMirrored, std::string& currentContDirID, unsigned maxOutIDs, int64_t lastHashDirOffset, int64_t lastContDirOffset) : BaseType(NETMSGTYPE_RetrieveFsIDs)`; `RetrieveFsIDsMsg() : BaseType(NETMSGTYPE_RetrieveFsIDs)`. Serialization writes `hashDirNum`, `buddyMirrored`, `rawString(obj->currentContDirID, obj->currentContDirIDLen)`, `maxOutIDs`, `lastHashDirOffset`, `lastContDirOffset`. Notable accessors/helpers include `getCurrentContDirID()`, `getHashDirNum()`, `getBuddyMirrored()`, `getLastContDirOffset()`, `getLastHashDirOffset()`, `getMaxOutIDs()`. Declared payload/backing members include `uint32_t hashDirNum`, `bool buddyMirrored`, `unsigned currentContDirIDLen`, `uint32_t maxOutIDs`, `int64_t lastHashDirOffset`, `int64_t lastContDirOffset`.

## Control Flow
Sender-side code builds `RetrieveFsIDsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/Path.h`, `common/storage/StorageDefinitions.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveFsIDs`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveFsIDs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveFsIDsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveFsIDsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveFsIDsRespMsg.h

## Purpose
Defines `RetrieveFsIDsRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_RetrieveFsIDsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RetrieveFsIDsRespMsg` derives from `public NetMessageSerdes<RetrieveFsIDsRespMsg>` and uses `BaseType(NETMSGTYPE_RetrieveFsIDsResp)` or an equivalent base constructor. Constructors include `RetrieveFsIDsRespMsg(FsckFsIDList* fsckFsIDs, std::string& currentContDirID, int64_t newHashDirOffset, int64_t newContDirOffset) : BaseType(NETMSGTYPE_RetrieveFsIDsResp)`; `RetrieveFsIDsRespMsg() : BaseType(NETMSGTYPE_RetrieveFsIDsResp)`. Serialization writes `rawString(obj->currentContDirID, obj->currentContDirIDLen, 4)`, `newHashDirOffset`, `newContDirOffset`, `backedPtr(obj->fsckFsIDs, obj->parsed.fsckFsIDs)`. Notable accessors/helpers include `getFsIDs()`, `getNewHashDirOffset()`, `getNewContDirOffset()`, `getCurrentContDirID()`. Declared payload/backing members include `const char* currentContDirID`, `unsigned currentContDirIDLen`, `int64_t newHashDirOffset`, `int64_t newContDirOffset`, `FsckFsIDList* fsckFsIDs`, `FsckFsIDList fsckFsIDs`.

## Control Flow
Sender-side code builds `RetrieveFsIDsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/fsck/FsckFsID.h`, `common/net/message/NetMessage.h`, `common/toolkit/ListTk.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveFsIDsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveFsIDsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveFsIDsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveInodesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveInodesMsg.h

## Purpose
Defines `RetrieveInodesMsg`, a BeeGFS fsck repair and audit query/request message using `NETMSGTYPE_RetrieveInodes`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RetrieveInodesMsg` derives from `public NetMessageSerdes<RetrieveInodesMsg>` and uses `BaseType(NETMSGTYPE_RetrieveInodes)` or an equivalent base constructor. Constructors include `RetrieveInodesMsg(unsigned hashDirNum, int64_t lastOffset, unsigned maxOutInodes, bool isBuddyMirrored): BaseType(NETMSGTYPE_RetrieveInodes), hashDirNum(hashDirNum), lastOffset(lastOffset), maxOutInodes(maxOutInodes), isBuddyMirrored(isBuddyMirrored)`; `RetrieveInodesMsg() : BaseType(NETMSGTYPE_RetrieveInodes)`. Serialization writes `hashDirNum`, `lastOffset`, `maxOutInodes`, `isBuddyMirrored`. Notable accessors/helpers include `isBuddyMirrored()`, `getHashDirNum()`, `getLastOffset()`, `getMaxOutInodes()`, `getIsBuddyMirrored()`. Declared payload/backing members include `uint32_t hashDirNum`, `int64_t lastOffset`, `uint32_t maxOutInodes`, `bool isBuddyMirrored`.

## Control Flow
Sender-side code builds `RetrieveInodesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveInodes`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveInodes`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveInodesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveInodesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveInodesRespMsg.h

## Purpose
Defines `RetrieveInodesRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_RetrieveInodesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RetrieveInodesRespMsg` derives from `public NetMessageSerdes<RetrieveInodesRespMsg>` and uses `BaseType(NETMSGTYPE_RetrieveInodesResp)` or an equivalent base constructor. Constructors include `RetrieveInodesRespMsg(FsckFileInodeList *fileInodes, FsckDirInodeList *dirInodes, int64_t lastOffset) : BaseType(NETMSGTYPE_RetrieveInodesResp)`; `RetrieveInodesRespMsg() : BaseType(NETMSGTYPE_RetrieveInodesResp)`. Serialization writes `backedPtr(obj->fileInodes, obj->parsed.fileInodes)`, `backedPtr(obj->dirInodes, obj->parsed.dirInodes)`, `lastOffset`. Notable accessors/helpers include `getFileInodes()`, `getDirInodes()`, `getLastOffset()`. Declared payload/backing members include `FsckFileInodeList* fileInodes`, `FsckDirInodeList* dirInodes`, `int64_t lastOffset`, `FsckFileInodeList fileInodes`, `FsckDirInodeList dirInodes`.

## Control Flow
Sender-side code builds `RetrieveInodesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckDirInode.h`, `common/fsck/FsckFileInode.h`, `common/net/message/NetMessage.h`, `common/toolkit/ListTk.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveInodesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveInodesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveInodesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateDirAttribsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateDirAttribsMsg.h

## Purpose
Defines `UpdateDirAttribsMsg`, a BeeGFS fsck repair and audit command message using `NETMSGTYPE_UpdateDirAttribs`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UpdateDirAttribsMsg` derives from `public NetMessageSerdes<UpdateDirAttribsMsg>` and uses `BaseType(NETMSGTYPE_UpdateDirAttribs)` or an equivalent base constructor. Constructors include `UpdateDirAttribsMsg(FsckDirInodeList* inodes) : BaseType(NETMSGTYPE_UpdateDirAttribs)`; `UpdateDirAttribsMsg() : BaseType(NETMSGTYPE_UpdateDirAttribs)`. Serialization writes `backedPtr(obj->inodes, obj->parsed.inodes)`. Notable accessors/helpers include `getInodes()`. Declared payload/backing members include `FsckDirInodeList* inodes`, `FsckDirInodeList inodes`.

## Control Flow
Sender-side code builds `UpdateDirAttribsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_UpdateDirAttribs`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateDirAttribs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateDirAttribsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateDirAttribsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateDirAttribsRespMsg.h

## Purpose
Defines `UpdateDirAttribsRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_UpdateDirAttribsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UpdateDirAttribsRespMsg` derives from `public NetMessageSerdes<UpdateDirAttribsRespMsg>` and uses `BaseType(NETMSGTYPE_UpdateDirAttribsResp)` or an equivalent base constructor. Constructors include `UpdateDirAttribsRespMsg(FsckDirInodeList* failedInodes) : BaseType(NETMSGTYPE_UpdateDirAttribsResp)`; `UpdateDirAttribsRespMsg() : BaseType(NETMSGTYPE_UpdateDirAttribsResp)`. Serialization writes `backedPtr(obj->failedInodes, obj->parsed.failedInodes)`. Notable accessors/helpers include `getFailedInodes()`. Declared payload/backing members include `FsckDirInodeList* failedInodes`, `FsckDirInodeList failedInodes`.

## Control Flow
Sender-side code builds `UpdateDirAttribsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_UpdateDirAttribsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateDirAttribsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateDirAttribsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateFileAttribsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateFileAttribsMsg.h

## Purpose
Defines `UpdateFileAttribsMsg`, a BeeGFS fsck repair and audit command message using `NETMSGTYPE_UpdateFileAttribs`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UpdateFileAttribsMsg` derives from `public NetMessageSerdes<UpdateFileAttribsMsg>` and uses `BaseType(NETMSGTYPE_UpdateFileAttribs)` or an equivalent base constructor. Constructors include `UpdateFileAttribsMsg(FsckFileInodeList* inodes) : BaseType(NETMSGTYPE_UpdateFileAttribs)`; `UpdateFileAttribsMsg() : BaseType(NETMSGTYPE_UpdateFileAttribs)`. Serialization writes `backedPtr(obj->inodes, obj->parsed.inodes)`. Notable accessors/helpers include `getInodes()`. Declared payload/backing members include `FsckFileInodeList* inodes`, `FsckFileInodeList inodes`.

## Control Flow
Sender-side code builds `UpdateFileAttribsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckFileInode.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_UpdateFileAttribs`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateFileAttribs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateFileAttribsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateFileAttribsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateFileAttribsRespMsg.h

## Purpose
Defines `UpdateFileAttribsRespMsg`, the response payload wrapper for BeeGFS fsck repair and audit RPCs using `NETMSGTYPE_UpdateFileAttribsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UpdateFileAttribsRespMsg` derives from `public NetMessageSerdes<UpdateFileAttribsRespMsg>` and uses `BaseType(NETMSGTYPE_UpdateFileAttribsResp)` or an equivalent base constructor. Constructors include `UpdateFileAttribsRespMsg(FsckFileInodeList* failedInodes) : BaseType(NETMSGTYPE_UpdateFileAttribsResp)`; `UpdateFileAttribsRespMsg() : BaseType(NETMSGTYPE_UpdateFileAttribsResp)`. Serialization writes `backedPtr(obj->failedInodes, obj->parsed.failedInodes)`. Notable accessors/helpers include `getFailedInodes()`. Declared payload/backing members include `FsckFileInodeList* failedInodes`, `FsckFileInodeList failedInodes`.

## Control Flow
Sender-side code builds `UpdateFileAttribsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckFileInode.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_UpdateFileAttribsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateFileAttribsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateFileAttribsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameMsg.h

## Purpose
Defines `GetHostByNameMsg`, a BeeGFS helper daemon query/request message using `NETMSGTYPE_GetHostByName`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetHostByNameMsg` derives from `public NetMessageSerdes<GetHostByNameMsg>` and uses `BaseType(NETMSGTYPE_GetHostByName)` or an equivalent base constructor. Constructors include `GetHostByNameMsg(const char* hostname) : BaseType(NETMSGTYPE_GetHostByName)`; `GetHostByNameMsg() : BaseType(NETMSGTYPE_GetHostByName)`. Serialization writes `rawString(obj->hostname, obj->hostnameLen)`. Notable accessors/helpers include `getHostname()`. Declared payload/backing members include `unsigned hostnameLen`, `const char* hostname`.

## Control Flow
Sender-side code builds `GetHostByNameMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_GetHostByName`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetHostByName`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameRespMsg.h

## Purpose
Defines `GetHostByNameRespMsg`, the response payload wrapper for BeeGFS helper daemon RPCs using `NETMSGTYPE_GetHostByNameResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetHostByNameRespMsg` derives from `public NetMessageSerdes<GetHostByNameRespMsg>` and uses `BaseType(NETMSGTYPE_GetHostByNameResp)` or an equivalent base constructor. Constructors include `GetHostByNameRespMsg(const char* hostAddr) : BaseType(NETMSGTYPE_GetHostByNameResp)`; `GetHostByNameRespMsg() : BaseType(NETMSGTYPE_GetHostByNameResp)`. Serialization writes `rawString(obj->hostAddr, obj->hostAddrLen)`. Notable accessors/helpers include `getHostAddr()`. Declared payload/backing members include `unsigned hostAddrLen`, `const char* hostAddr`.

## Control Flow
Sender-side code builds `GetHostByNameRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_GetHostByNameResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetHostByNameResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogMsg.h

## Purpose
Defines `LogMsg`, a BeeGFS helper daemon command message using `NETMSGTYPE_Log`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`LogMsg` derives from `public NetMessageSerdes<LogMsg>` and uses `BaseType(NETMSGTYPE_Log)` or an equivalent base constructor. Constructors include `LogMsg(int level, int threadID, const char* threadName, const char* context, const char* logMsg) : BaseType(NETMSGTYPE_Log)`; `LogMsg() : BaseType(NETMSGTYPE_Log)`. Serialization writes `level`, `threadID`, `rawString(obj->threadName, obj->threadNameLen)`, `rawString(obj->context, obj->contextLen)`, `rawString(obj->logMsg, obj->logMsgLen)`. Notable accessors/helpers include `getLevel()`, `getThreadID()`, `getThreadName()`, `getContext()`, `getLogMsg()`. Declared payload/backing members include `int32_t level`, `int32_t threadID`, `unsigned threadNameLen`, `const char* threadName`, `unsigned contextLen`, `const char* context`, `unsigned logMsgLen`, `const char* logMsg`.

## Control Flow
Sender-side code builds `LogMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_Log`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_Log`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogRespMsg.h

## Purpose
Defines `LogRespMsg`, the response payload wrapper for BeeGFS helper daemon RPCs using `NETMSGTYPE_LogResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`LogRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_LogResp)` or an equivalent base constructor. Constructors include `LogRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_LogResp, result)`; `LogRespMsg() : SimpleIntMsg(NETMSGTYPE_LogResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `LogRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_LogResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_LogResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestMetaDataMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestMetaDataMsg.h

## Purpose
Defines `RequestMetaDataMsg`, a BeeGFS monitoring query/request message using `NETMSGTYPE_RequestMetaData`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RequestMetaDataMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_RequestMetaData)` or an equivalent base constructor. Constructors include `RequestMetaDataMsg(int64_t lastStatsTimeMS) : SimpleInt64Msg (NETMSGTYPE_RequestMetaData, lastStatsTimeMS)`; `RequestMetaDataMsg() : SimpleInt64Msg(NETMSGTYPE_RequestMetaData,0)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RequestMetaDataMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`, `common/net/message/NetMessageTypes.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the monitoring code path that handles `NETMSGTYPE_RequestMetaData`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RequestMetaData`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestMetaDataMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestMetaDataRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestMetaDataRespMsg.h

## Purpose
Defines `RequestMetaDataRespMsg`, the response payload wrapper for BeeGFS monitoring RPCs using `NETMSGTYPE_RequestMetaDataResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RequestMetaDataRespMsg` derives from `public NetMessageSerdes<RequestMetaDataRespMsg>` and uses `BaseType(NETMSGTYPE_RequestMetaDataResp)` or an equivalent base constructor. Constructors include `RequestMetaDataRespMsg(const std::string& nodeID, const std::string& hostnameid, NumNodeID nodeNumID, NicAddressList *nicList, bool isRoot, unsigned IndirectWorkListSize, unsigned DirectWorkListSize, unsigned sessionCount, HighResStatsList* statsList) : BaseType(NETMSGTYPE_RequestMetaDataResp)`; `RequestMetaDataRespMsg() : BaseType(NETMSGTYPE_RequestMetaDataResp)`. Serialization writes `nodeID`, `hostnameid`, `nodeNumID`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `isRoot`, `indirectWorkListSize`, `directWorkListSize`, `sessionCount`, `backedPtr(obj->statsList, obj->parsed.statsList)`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getNicList()`, `getStatsList()`, `getNodeID()`, `gethostnameid()`, `getNodeNumID()`, `getIsRoot()`, `getIndirectWorkListSize()`, `getDirectWorkListSize()`, `getSessionCount()`. Declared payload/backing members include `static const unsigned USE_CLIENT_STATS_V2`, `std::string nodeID`, `std::string hostnameid`, `NumNodeID nodeNumID`, `bool isRoot`, `uint32_t indirectWorkListSize`, `uint32_t directWorkListSize`, `uint32_t sessionCount`, `NicAddressList* nicList`, `HighResStatsList* statsList`, `HighResStatsList statsList`, `NicAddressList nicList`.

## Control Flow
Sender-side code builds `RequestMetaDataRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the monitoring code path that handles `NETMSGTYPE_RequestMetaDataResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RequestMetaDataResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestMetaDataRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestStorageDataMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestStorageDataMsg.h

## Purpose
Defines `RequestStorageDataMsg`, a BeeGFS monitoring query/request message using `NETMSGTYPE_RequestStorageData`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RequestStorageDataMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_RequestStorageData)` or an equivalent base constructor. Constructors include `RequestStorageDataMsg(int64_t lastStatsTimeMS) : SimpleInt64Msg(NETMSGTYPE_RequestStorageData, lastStatsTimeMS)`; `RequestStorageDataMsg() : SimpleInt64Msg(NETMSGTYPE_RequestStorageData,0)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RequestStorageDataMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`, `common/net/message/NetMessageTypes.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the monitoring code path that handles `NETMSGTYPE_RequestStorageData`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RequestStorageData`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestStorageDataMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestStorageDataRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestStorageDataRespMsg.h

## Purpose
Defines `RequestStorageDataRespMsg`, the response payload wrapper for BeeGFS monitoring RPCs using `NETMSGTYPE_RequestStorageDataResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RequestStorageDataRespMsg` derives from `public NetMessageSerdes<RequestStorageDataRespMsg>` and uses `BaseType(NETMSGTYPE_RequestStorageDataResp)` or an equivalent base constructor. Constructors include `RequestStorageDataRespMsg(const std::string& nodeID, const std::string& hostnameid, NumNodeID nodeNumID, NicAddressList *nicList, unsigned indirectWorkListSize, unsigned directWorkListSize, int64_t diskSpaceTotal, int64_t diskSpaceFree, unsigned sessionCount, HighResStatsList* statsList, StorageTargetInfoList *storageTargets) : BaseType(NETMSGTYPE_RequestStorageDataResp)`; `RequestStorageDataRespMsg() : BaseType(NETMSGTYPE_RequestStorageDataResp)`. Serialization writes `nodeID`, `hostnameid`, `nodeNumID`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `indirectWorkListSize`, `directWorkListSize`, `diskSpaceTotalMiB`, `diskSpaceFreeMiB`, `sessionCount`, `backedPtr(obj->statsList, obj->parsed.statsList)`, `backedPtr(obj->storageTargets, obj->parsed.storageTargets)`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getNicList()`, `getStatsList()`, `getStorageTargets()`, `getNodeID()`, `gethostnameid()`, `getNodeNumID()`, `getIndirectWorkListSize()`, `getDirectWorkListSize()`, `getDiskSpaceTotalMiB()`, `getDiskSpaceFreeMiB()`, `getSessionCount()`. Declared payload/backing members include `static const unsigned NODE_SUPPORTS_IPV6`, `std::string nodeID`, `std::string hostnameid`, `NumNodeID nodeNumID`, `NicAddressList* nicList`, `uint32_t indirectWorkListSize`, `uint32_t directWorkListSize`, `int64_t diskSpaceTotalMiB`, `int64_t diskSpaceFreeMiB`, `uint32_t sessionCount`, `StorageTargetInfoList storageTargets`, `HighResStatsList statsList`, `NicAddressList nicList`, `HighResStatsList* statsList`.

## Control Flow
Sender-side code builds `RequestStorageDataRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/storage/StorageDefinitions.h`, `common/storage/StorageTargetInfo.h`, `common/toolkit/HighResolutionStats.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the monitoring code path that handles `NETMSGTYPE_RequestStorageDataResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RequestStorageDataResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestStorageDataRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/ChangeTargetConsistencyStatesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/ChangeTargetConsistencyStatesMsg.h

## Purpose
Defines `ChangeTargetConsistencyStatesMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_ChangeTargetConsistencyStates`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ChangeTargetConsistencyStatesMsg` derives from `public AcknowledgeableMsgSerdes<ChangeTargetConsistencyStatesMsg>` and uses `BaseType(NETMSGTYPE_ChangeTargetConsistencyStates)` or an equivalent base constructor. Constructors include `ChangeTargetConsistencyStatesMsg(NodeType nodeType, UInt16List* targetIDs, UInt8List* oldStates, UInt8List* newStates) : BaseType(NETMSGTYPE_ChangeTargetConsistencyStates), nodeType(nodeType), targetIDs(targetIDs), oldStates(oldStates), newStates(newStates)`; `ChangeTargetConsistencyStatesMsg() : BaseType(NETMSGTYPE_ChangeTargetConsistencyStates)`. Serialization writes `nodeType`, `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`, `backedPtr(obj->oldStates, obj->parsed.oldStates)`, `backedPtr(obj->newStates, obj->parsed.newStates)`. Notable accessors/helpers include `serializeAckID()`, `getNodeType()`, `getTargetIDs()`, `getOldStates()`, `getNewStates()`. Declared payload/backing members include `int32_t nodeType`, `UInt16List* targetIDs`, `UInt8List* oldStates`, `UInt8List* newStates`, `UInt16List targetIDs`, `UInt8List oldStates`, `UInt8List newStates`.

## Control Flow
Sender-side code builds `ChangeTargetConsistencyStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_ChangeTargetConsistencyStates`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ChangeTargetConsistencyStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/ChangeTargetConsistencyStatesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/ChangeTargetConsistencyStatesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/ChangeTargetConsistencyStatesRespMsg.h

## Purpose
Defines `ChangeTargetConsistencyStatesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_ChangeTargetConsistencyStatesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`ChangeTargetConsistencyStatesRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_ChangeTargetConsistencyStatesResp)` or an equivalent base constructor. Constructors include `ChangeTargetConsistencyStatesRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_ChangeTargetConsistencyStatesResp, result)`; `ChangeTargetConsistencyStatesRespMsg() : SimpleIntMsg(NETMSGTYPE_ChangeTargetConsistencyStatesResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `ChangeTargetConsistencyStatesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_ChangeTargetConsistencyStatesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ChangeTargetConsistencyStatesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/ChangeTargetConsistencyStatesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GenericDebugMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GenericDebugMsg.h

## Purpose
Defines `GenericDebugMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_GenericDebug`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`GenericDebugMsg` derives from `public SimpleStringMsg` and uses `BaseType(NETMSGTYPE_GenericDebug)` or an equivalent base constructor. Constructors include `GenericDebugMsg(const char* commandStr) : SimpleStringMsg(NETMSGTYPE_GenericDebug, commandStr)`; `GenericDebugMsg() : SimpleStringMsg(NETMSGTYPE_GenericDebug)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getCommandStr()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GenericDebugMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleStringMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GenericDebug`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GenericDebug`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GenericDebugMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GenericDebugRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GenericDebugRespMsg.h

## Purpose
Defines `GenericDebugRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GenericDebugResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GenericDebugRespMsg` derives from `public SimpleStringMsg` and uses `BaseType(NETMSGTYPE_GenericDebugResp)` or an equivalent base constructor. Constructors include `GenericDebugRespMsg(const char* cmdRespStr) : SimpleStringMsg(NETMSGTYPE_GenericDebugResp, cmdRespStr)`; `GenericDebugRespMsg() : SimpleStringMsg(NETMSGTYPE_GenericDebugResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getCmdRespStr()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GenericDebugRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleStringMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GenericDebugResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GenericDebugResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GenericDebugRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsMsg.h

## Purpose
Defines `GetClientStatsMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetClientStats`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetClientStatsMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_GetClientStats)` or an equivalent base constructor. Constructors include `GetClientStatsMsg(int64_t cookie) : SimpleInt64Msg(NETMSGTYPE_GetClientStats, cookie)`; `GetClientStatsMsg() : SimpleInt64Msg(NETMSGTYPE_GetClientStats)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getCookieIP()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetClientStatsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetClientStats`. Feature flags: `GETCLIENTSTATSMSG_FLAG_PERUSERSTATS`=1.

## Risks And Edge Cases
Feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetClientStats`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsRespMsg.h

## Purpose
Defines `GetClientStatsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetClientStatsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetClientStatsRespMsg` derives from `public NetMessageSerdes<GetClientStatsRespMsg>` and uses `BaseType(NETMSGTYPE_GetClientStatsResp)` or an equivalent base constructor. Constructors include `GetClientStatsRespMsg(UInt64Vector* statsVec) : BaseType(NETMSGTYPE_GetClientStatsResp)`; `GetClientStatsRespMsg() : BaseType(NETMSGTYPE_GetClientStatsResp)`. Serialization writes `backedPtr(obj->statsVec, obj->parsed.statsVec)`. Notable accessors/helpers include `getStatsVector()`. Declared payload/backing members include `UInt64Vector* statsVec`, `UInt64Vector statsVec`.

## Control Flow
Sender-side code builds `GetClientStatsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/HighResolutionStats.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetClientStatsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetClientStatsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsV2Msg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsV2Msg.h

## Purpose
Defines `GetClientStatsV2Msg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetClientStatsV2`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetClientStatsV2Msg` derives from `public NetMessageSerdes<GetClientStatsV2Msg>` and uses `BaseType(NETMSGTYPE_GetClientStatsV2)` or an equivalent base constructor. Constructors include `GetClientStatsV2Msg(uint128_t cookie) : BaseType(NETMSGTYPE_GetClientStatsV2), cookie(cookie)`; `GetClientStatsV2Msg() : BaseType(NETMSGTYPE_GetClientStatsV2)`. Serialization writes `cookie`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getCookieIP()`. Declared payload/backing members include `uint128_t cookie`.

## Control Flow
Sender-side code builds `GetClientStatsV2Msg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/message/SimpleInt64Msg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetClientStatsV2`. Feature flags: `GETCLIENTSTATSMSG_FLAG_PERUSERSTATS`=1.

## Risks And Edge Cases
Feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetClientStatsV2`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsV2Msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsV2RespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsV2RespMsg.h

## Purpose
Defines `GetClientStatsV2RespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetClientStatsV2Resp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetClientStatsV2RespMsg` derives from `public NetMessageSerdes<GetClientStatsV2RespMsg>` and uses `BaseType(NETMSGTYPE_GetClientStatsV2Resp)` or an equivalent base constructor. Constructors include `GetClientStatsV2RespMsg(Uint128Vector* statsVec) : BaseType(NETMSGTYPE_GetClientStatsV2Resp)`; `GetClientStatsV2RespMsg() : BaseType(NETMSGTYPE_GetClientStatsV2Resp)`. Serialization writes `backedPtr(obj->statsVec, obj->parsed.statsVec)`. Notable accessors/helpers include `getStatsVector()`. Declared payload/backing members include `Uint128Vector* statsVec`, `Uint128Vector statsVec`.

## Control Flow
Sender-side code builds `GetClientStatsV2RespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/HighResolutionStats.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetClientStatsV2Resp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetClientStatsV2Resp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsV2RespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetMirrorBuddyGroupsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetMirrorBuddyGroupsMsg.h

## Purpose
Defines `GetMirrorBuddyGroupsMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetMirrorBuddyGroups`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetMirrorBuddyGroupsMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_GetMirrorBuddyGroups)` or an equivalent base constructor. Constructors include `GetMirrorBuddyGroupsMsg(NodeType nodeType) : SimpleIntMsg(NETMSGTYPE_GetMirrorBuddyGroups, nodeType)`; `GetMirrorBuddyGroupsMsg() : SimpleIntMsg(NETMSGTYPE_GetMirrorBuddyGroups)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getNodeType()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetMirrorBuddyGroupsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetMirrorBuddyGroups`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetMirrorBuddyGroups`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetMirrorBuddyGroupsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetMirrorBuddyGroupsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetMirrorBuddyGroupsRespMsg.h

## Purpose
Defines `GetMirrorBuddyGroupsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetMirrorBuddyGroupsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetMirrorBuddyGroupsRespMsg` derives from `public NetMessageSerdes<GetMirrorBuddyGroupsRespMsg>` and uses `BaseType(NETMSGTYPE_GetMirrorBuddyGroupsResp)` or an equivalent base constructor. Constructors include `GetMirrorBuddyGroupsRespMsg(UInt16List* buddyGroupIDs, UInt16List* primaryTargetIDs, UInt16List* secondaryTargetIDs) : BaseType(NETMSGTYPE_GetMirrorBuddyGroupsResp)`; `GetMirrorBuddyGroupsRespMsg() : BaseType(NETMSGTYPE_GetMirrorBuddyGroupsResp)`. Serialization writes `backedPtr(obj->buddyGroupIDs, obj->parsed.buddyGroupIDs)`, `backedPtr(obj->primaryTargetIDs, obj->parsed.primaryTargetIDs)`, `backedPtr(obj->secondaryTargetIDs, obj->parsed.secondaryTargetIDs)`. Notable accessors/helpers include `getBuddyGroupIDs()`, `getPrimaryTargetIDs()`, `getSecondaryTargetIDs()`. Declared payload/backing members include `UInt16List* buddyGroupIDs`, `UInt16List* primaryTargetIDs`, `UInt16List* secondaryTargetIDs`, `UInt16List buddyGroupIDs`, `UInt16List primaryTargetIDs`, `UInt16List secondaryTargetIDs`.

## Control Flow
Sender-side code builds `GetMirrorBuddyGroupsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetMirrorBuddyGroupsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetMirrorBuddyGroupsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetMirrorBuddyGroupsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodeCapacityPoolsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodeCapacityPoolsMsg.h

## Purpose
Defines `GetNodeCapacityPoolsMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetNodeCapacityPools`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetNodeCapacityPoolsMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_GetNodeCapacityPools)` or an equivalent base constructor. Constructors include `GetNodeCapacityPoolsMsg(CapacityPoolQueryType poolType) : SimpleIntMsg(NETMSGTYPE_GetNodeCapacityPools, poolType)`; `GetNodeCapacityPoolsMsg() : SimpleIntMsg(NETMSGTYPE_GetNodeCapacityPools)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getCapacityPoolQueryType()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetNodeCapacityPoolsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `../SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetNodeCapacityPools`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetNodeCapacityPools`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodeCapacityPoolsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodeCapacityPoolsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodeCapacityPoolsRespMsg.h

## Purpose
Defines `GetNodeCapacityPoolsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetNodeCapacityPoolsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetNodeCapacityPoolsRespMsg` derives from `public NetMessageSerdes<GetNodeCapacityPoolsRespMsg>` and uses `BaseType(NETMSGTYPE_GetNodeCapacityPoolsResp)` or an equivalent base constructor. Constructors include `GetNodeCapacityPoolsRespMsg(PoolsMap* poolsMap) : BaseType(NETMSGTYPE_GetNodeCapacityPoolsResp), poolsMap(poolsMap)`; `GetNodeCapacityPoolsRespMsg() : BaseType(NETMSGTYPE_GetNodeCapacityPoolsResp)`. Serialization writes `backedPtr(obj->poolsMap, obj->parsed.poolsMap)`. Notable accessors/helpers include `getPoolsMap()`. Declared payload/backing members include `PoolsMap* poolsMap`, `PoolsMap poolsMap`.

## Control Flow
Sender-side code builds `GetNodeCapacityPoolsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetNodeCapacityPoolsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetNodeCapacityPoolsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodeCapacityPoolsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodesMsg.h

## Purpose
Defines `GetNodesMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetNodes`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetNodesMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_GetNodes)` or an equivalent base constructor. Constructors include `GetNodesMsg(NodeType nodeType) : SimpleIntMsg(NETMSGTYPE_GetNodes, nodeType)`; `GetNodesMsg() : SimpleIntMsg(NETMSGTYPE_GetNodes)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getNodeType()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetNodesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetNodes`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetNodes`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodesRespMsg.h

## Purpose
Defines `GetNodesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetNodesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetNodesRespMsg` derives from `public NetMessageSerdes<GetNodesRespMsg>` and uses `BaseType(NETMSGTYPE_GetNodesResp)` or an equivalent base constructor. Constructors include `GetNodesRespMsg(NumNodeID rootNumID, bool rootIsBuddyMirrored, std::vector<NodeHandle>& nodeList) : BaseType(NETMSGTYPE_GetNodesResp)`; `GetNodesRespMsg() : BaseType(NETMSGTYPE_GetNodesResp)`. Serialization writes `backedPtr(obj->nodeList, obj->parsed.nodeList)`, `rootNumID`, `rootIsBuddyMirrored`. Notable accessors/helpers include `getNodeList()`, `getRootNumID()`, `getRootIsBuddyMirrored()`. Declared payload/backing members include `NumNodeID rootNumID`, `bool rootIsBuddyMirrored`, `std::vector<NodeHandle>* nodeList`, `std::vector<NodeHandle> nodeList`.

## Control Flow
Sender-side code builds `GetNodesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetNodesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetNodesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetNodesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h

## Purpose
Defines `GetStatesAndBuddyGroupsMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetStatesAndBuddyGroups`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetStatesAndBuddyGroupsMsg` derives from `public NetMessageSerdes<GetStatesAndBuddyGroupsMsg>` and uses `BaseType(NETMSGTYPE_GetStatesAndBuddyGroups)` or an equivalent base constructor. Constructors include `GetStatesAndBuddyGroupsMsg(NodeType nodeType) : BaseType(NETMSGTYPE_GetStatesAndBuddyGroups), nodeType(nodeType), requestedByClientID(NumNodeID(0))`; `GetStatesAndBuddyGroupsMsg() : BaseType(NETMSGTYPE_GetStatesAndBuddyGroups)`. Serialization writes `nodeType`, `requestedByClientID`. Notable accessors/helpers include `getNodeType()`, `getRequestedByClientID()`. Declared payload/backing members include `int32_t nodeType`, `NumNodeID requestedByClientID`.

## Control Flow
Sender-side code builds `GetStatesAndBuddyGroupsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/nodes/NumNodeID.h`, `common/net/message/SimpleIntMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetStatesAndBuddyGroups`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetStatesAndBuddyGroups`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h

## Purpose
Defines `GetStatesAndBuddyGroupsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetStatesAndBuddyGroupsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetStatesAndBuddyGroupsRespMsg` derives from `public NetMessageSerdes<GetStatesAndBuddyGroupsRespMsg>` and uses `BaseType(NETMSGTYPE_GetStatesAndBuddyGroupsResp)` or an equivalent base constructor. Constructors include `GetStatesAndBuddyGroupsRespMsg(const MirrorBuddyGroupMap& groups, const TargetStateMap& states) : BaseType(NETMSGTYPE_GetStatesAndBuddyGroupsResp), groups(&groups), states(&states)`; `GetStatesAndBuddyGroupsRespMsg() : BaseType(NETMSGTYPE_GetStatesAndBuddyGroupsResp)`. Serialization writes `backedPtr(obj->groups, obj->parsed.groups)`, `backedPtr(obj->states, obj->parsed.states)`. Notable accessors/helpers include `getGroups()`, `getStates()`. Declared payload/backing members include `const MirrorBuddyGroupMap* groups`, `const TargetStateMap* states`, `MirrorBuddyGroupMap groups`, `TargetStateMap states`.

## Control Flow
Sender-side code builds `GetStatesAndBuddyGroupsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`, `common/nodes/MirrorBuddyGroup.h`, `common/nodes/TargetStateInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetStatesAndBuddyGroupsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetStatesAndBuddyGroupsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetConsistencyStatesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetConsistencyStatesMsg.h

## Purpose
Defines `GetTargetConsistencyStatesMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetTargetConsistencyStates`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetTargetConsistencyStatesMsg` derives from `public NetMessageSerdes<GetTargetConsistencyStatesMsg>` and uses `BaseType(NETMSGTYPE_GetTargetConsistencyStates)` or an equivalent base constructor. Constructors include `GetTargetConsistencyStatesMsg(const UInt16Vector& targetIDs) : BaseType(NETMSGTYPE_GetTargetConsistencyStates), targetIDs(targetIDs)`; `GetTargetConsistencyStatesMsg() : BaseType(NETMSGTYPE_GetTargetConsistencyStates)`. Serialization writes `targetIDs`. Declared payload/backing members include `UInt16Vector targetIDs`.

## Control Flow
Sender-side code builds `GetTargetConsistencyStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Depends primarily on the BeeGFS `NetMessage` serialization framework. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetConsistencyStates`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetConsistencyStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetConsistencyStatesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetConsistencyStatesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetConsistencyStatesRespMsg.h

## Purpose
Defines `GetTargetConsistencyStatesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetTargetConsistencyStatesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetTargetConsistencyStatesRespMsg` derives from `public NetMessageSerdes<GetTargetConsistencyStatesRespMsg>` and uses `BaseType(NETMSGTYPE_GetTargetConsistencyStatesResp)` or an equivalent base constructor. Constructors include `GetTargetConsistencyStatesRespMsg(const TargetConsistencyStateVec& states) : BaseType(NETMSGTYPE_GetTargetConsistencyStatesResp), states(states)`; `GetTargetConsistencyStatesRespMsg() : BaseType(NETMSGTYPE_GetTargetConsistencyStatesResp)`. Serialization writes `states`. Notable accessors/helpers include `getStates()`. Declared payload/backing members include `TargetConsistencyStateVec states`.

## Control Flow
Sender-side code builds `GetTargetConsistencyStatesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Depends primarily on the BeeGFS `NetMessage` serialization framework. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetConsistencyStatesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetConsistencyStatesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetConsistencyStatesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetMappingsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetMappingsMsg.h

## Purpose
Defines `GetTargetMappingsMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetTargetMappings`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetTargetMappingsMsg` derives from `public SimpleMsg` and uses `BaseType(NETMSGTYPE_GetTargetMappings)` or an equivalent base constructor. Constructors include `GetTargetMappingsMsg() : SimpleMsg(NETMSGTYPE_GetTargetMappings)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetTargetMappingsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetMappings`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetMappings`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetMappingsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetMappingsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetMappingsRespMsg.h

## Purpose
Defines `GetTargetMappingsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetTargetMappingsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetTargetMappingsRespMsg` derives from `public NetMessageSerdes<GetTargetMappingsRespMsg>` and uses `BaseType(NETMSGTYPE_GetTargetMappingsResp)` or an equivalent base constructor. Constructors include `GetTargetMappingsRespMsg(const std::map<uint16_t, NumNodeID>& mappings) : BaseType(NETMSGTYPE_GetTargetMappingsResp), mappings(&mappings)`; `GetTargetMappingsRespMsg() : BaseType(NETMSGTYPE_GetTargetMappingsResp)`. Serialization writes `backedPtr(obj->mappings, obj->parsed.mappings)`. Notable accessors/helpers include `getMappings()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetTargetMappingsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetMappingsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetMappingsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetMappingsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetStatesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetStatesMsg.h

## Purpose
Defines `GetTargetStatesMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetTargetStates`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetTargetStatesMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_GetTargetStates)` or an equivalent base constructor. Constructors include `GetTargetStatesMsg(NodeType nodeType) : SimpleIntMsg(NETMSGTYPE_GetTargetStates, nodeType)`; `GetTargetStatesMsg() : SimpleIntMsg(NETMSGTYPE_GetTargetStates)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getNodeType()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetTargetStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetStates`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetStatesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetStatesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetStatesRespMsg.h

## Purpose
Defines `GetTargetStatesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetTargetStatesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetTargetStatesRespMsg` derives from `public NetMessageSerdes<GetTargetStatesRespMsg>` and uses `BaseType(NETMSGTYPE_GetTargetStatesResp)` or an equivalent base constructor. Constructors include `GetTargetStatesRespMsg(UInt16List* targetIDs, UInt8List* reachabilityStates, UInt8List* consistencyStates) : BaseType(NETMSGTYPE_GetTargetStatesResp)`; `GetTargetStatesRespMsg() : BaseType(NETMSGTYPE_GetTargetStatesResp)`. Serialization writes `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`, `backedPtr(obj->reachabilityStates, obj->parsed.reachabilityStates)`, `backedPtr(obj->consistencyStates, obj->parsed.consistencyStates)`. Notable accessors/helpers include `getTargetIDs()`, `getReachabilityStates()`, `getConsistencyStates()`. Declared payload/backing members include `UInt16List* targetIDs`, `UInt8List* reachabilityStates`, `UInt8List* consistencyStates`, `UInt16List targetIDs`, `UInt8List reachabilityStates`, `UInt8List consistencyStates`.

## Control Flow
Sender-side code builds `GetTargetStatesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`, `common/nodes/TargetStateStore.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetTargetStatesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetTargetStatesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetTargetStatesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/HeartbeatMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/HeartbeatMsg.h

## Purpose
Defines `HeartbeatMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_Heartbeat`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`HeartbeatMsg` derives from `public AcknowledgeableMsgSerdes<HeartbeatMsg>` and uses `BaseType(NETMSGTYPE_Heartbeat)` or an equivalent base constructor. Constructors include `HeartbeatMsg(const std::string& nodeID, NumNodeID nodeNumID, NodeType nodeType, NicAddressList* nicList) : BaseType(NETMSGTYPE_Heartbeat)`; `HeartbeatMsg() : BaseType(NETMSGTYPE_Heartbeat)`. Serialization writes `instanceVersion`, `nicListVersion`, `nodeType`, `nodeID`, `nodeNumID`, `rootNumID`, `rootIsBuddyMirrored`, `portUDP`, `portTCP`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `machineUUID`. Notable accessors/helpers include `serializeAckID()`, `getNicList()`, `getNodeID()`, `getNodeNumID()`, `getNodeType()`, `getRootNumID()`, `setRootNumID()`, `getRootIsBuddyMirrored()`, `setRootIsBuddyMirrored()`, `setPorts()`, `setMachineUUID()`, `getPortUDP()`, and additional getters/setters. Declared payload/backing members include `std::string nodeID`, `std::string machineUUID`, `int32_t nodeType`, `NumNodeID nodeNumID`, `NumNodeID rootNumID`, `bool rootIsBuddyMirrored`, `uint64_t instanceVersion`, `uint64_t nicListVersion`, `uint16_t portUDP`, `uint16_t portTCP`, `NicAddressList* nicList`, `NicAddressList nicList`.

## Control Flow
Sender-side code builds `HeartbeatMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/net/sock/NetworkInterfaceCard.h`, `common/nodes/Node.h`, `common/Common.h`, `iostream`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_Heartbeat`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_Heartbeat`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/HeartbeatMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/HeartbeatRequestMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/HeartbeatRequestMsg.h

## Purpose
Defines `HeartbeatRequestMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_HeartbeatRequest`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`HeartbeatRequestMsg` derives from `public SimpleMsg` and uses `BaseType(NETMSGTYPE_HeartbeatRequest)` or an equivalent base constructor. Constructors include `HeartbeatRequestMsg() : SimpleMsg(NETMSGTYPE_HeartbeatRequest)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `HeartbeatRequestMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `../SimpleMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_HeartbeatRequest`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_HeartbeatRequest`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/HeartbeatRequestMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsMsg.h

## Purpose
Defines `MapTargetsMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_MapTargets`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`MapTargetsMsg` derives from `public AcknowledgeableMsgSerdes<MapTargetsMsg>` and uses `BaseType(NETMSGTYPE_MapTargets)` or an equivalent base constructor. Constructors include `MapTargetsMsg(const std::map<uint16_t, StoragePoolId>& targets, NumNodeID nodeID): BaseType(NETMSGTYPE_MapTargets), nodeID(nodeID), targets(&targets)`; `MapTargetsMsg() : BaseType(NETMSGTYPE_MapTargets)`. Serialization writes `backedPtr(obj->targets, obj->parsed.targets)`, `nodeID`. Notable accessors/helpers include `serializeAckID()`, `getNodeID()`, `getTargets()`. Declared payload/backing members include `NumNodeID nodeID`.

## Control Flow
Sender-side code builds `MapTargetsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/NumNodeID.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_MapTargets`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MapTargets`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsRespMsg.h

## Purpose
Defines `MapTargetsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_MapTargetsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MapTargetsRespMsg` derives from `public NetMessageSerdes<MapTargetsRespMsg>` and uses `BaseType(NETMSGTYPE_MapTargetsResp)` or an equivalent base constructor. Constructors include `MapTargetsRespMsg(const std::map<uint16_t, FhgfsOpsErr>& results): BaseType(NETMSGTYPE_MapTargetsResp), results(&results)`; `MapTargetsRespMsg(): BaseType(NETMSGTYPE_MapTargetsResp)`. Serialization writes `backedPtr(obj->results, obj->parsed.results)`. Notable accessors/helpers include `getResults()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `MapTargetsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_MapTargetsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MapTargetsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/MapTargetsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/PublishCapacitiesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/PublishCapacitiesMsg.h

## Purpose
Defines `PublishCapacitiesMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_PublishCapacities`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`PublishCapacitiesMsg` derives from `public AcknowledgeableMsgSerdes<PublishCapacitiesMsg>` and uses `BaseType(NETMSGTYPE_PublishCapacities)` or an equivalent base constructor. Constructors include `PublishCapacitiesMsg() : BaseType(NETMSGTYPE_PublishCapacities)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `PublishCapacitiesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_PublishCapacities`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_PublishCapacities`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/PublishCapacitiesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RefreshCapacityPoolsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RefreshCapacityPoolsMsg.h

## Purpose
Defines `RefreshCapacityPoolsMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RefreshCapacityPools`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RefreshCapacityPoolsMsg` derives from `public AcknowledgeableMsgSerdes<RefreshCapacityPoolsMsg>` and uses `BaseType(NETMSGTYPE_RefreshCapacityPools)` or an equivalent base constructor. Constructors include `RefreshCapacityPoolsMsg() : BaseType(NETMSGTYPE_RefreshCapacityPools)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RefreshCapacityPoolsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RefreshCapacityPools`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshCapacityPools`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RefreshCapacityPoolsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RefreshTargetStatesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RefreshTargetStatesMsg.h

## Purpose
Defines `RefreshTargetStatesMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RefreshTargetStates`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RefreshTargetStatesMsg` derives from `public AcknowledgeableMsgSerdes<RefreshTargetStatesMsg>` and uses `BaseType(NETMSGTYPE_RefreshTargetStates)` or an equivalent base constructor. Constructors include `RefreshTargetStatesMsg() : BaseType(NETMSGTYPE_RefreshTargetStates)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RefreshTargetStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RefreshTargetStates`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshTargetStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RefreshTargetStatesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeMsg.h

## Purpose
Defines `RegisterNodeMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RegisterNode`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RegisterNodeMsg` derives from `public NetMessageSerdes<RegisterNodeMsg>` and uses `BaseType(NETMSGTYPE_RegisterNode)` or an equivalent base constructor. Constructors include `RegisterNodeMsg(const std::string& nodeID, NumNodeID nodeNumID, NodeType nodeType, NicAddressList* nicList, uint16_t portUDP, uint16_t portTCP) : BaseType(NETMSGTYPE_RegisterNode)`; `RegisterNodeMsg() : BaseType(NETMSGTYPE_RegisterNode)`. Serialization writes `instanceVersion`, `nicListVersion`, `nodeID`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `nodeType`, `nodeNumID`, `rootNumID`, `rootIsBuddyMirrored`, `portUDP`, `portTCP`, `machineUUID`. Notable accessors/helpers include `getNicList()`, `getNodeID()`, `getNodeNumID()`, `getNodeType()`, `getRootNumID()`, `setRootNumID()`, `getRootIsBuddyMirrored()`, `setRootIsBuddyMirrored()`, `setMachineUUID()`, `getPortUDP()`, `getPortTCP()`. Declared payload/backing members include `std::string nodeID`, `std::string machineUUID`, `int32_t nodeType`, `NumNodeID nodeNumID`, `NumNodeID rootNumID`, `bool rootIsBuddyMirrored`, `uint64_t instanceVersion`, `uint64_t nicListVersion`, `uint16_t portUDP`, `uint16_t portTCP`, `NicAddressList* nicList`, `NicAddressList nicList`.

## Control Flow
Sender-side code builds `RegisterNodeMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/sock/NetworkInterfaceCard.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RegisterNode`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RegisterNode`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeRespMsg.h

## Purpose
Defines `RegisterNodeRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_RegisterNodeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RegisterNodeRespMsg` derives from `public NetMessageSerdes<RegisterNodeRespMsg>` and uses `BaseType(NETMSGTYPE_RegisterNodeResp)` or an equivalent base constructor. Constructors include `RegisterNodeRespMsg(NumNodeID nodeNumID) : BaseType(NETMSGTYPE_RegisterNodeResp), nodeNumID(nodeNumID)`; `RegisterNodeRespMsg() : BaseType(NETMSGTYPE_RegisterNodeResp)`. Serialization writes `nodeNumID`, `grpcPort`, `fsUUID`. Notable accessors/helpers include `getNodeNumID()`. Declared payload/backing members include `NumNodeID nodeNumID`, `uint16_t grpcPort`, `std::string fsUUID`.

## Control Flow
Sender-side code builds `RegisterNodeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `stdint.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RegisterNodeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RegisterNodeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterNodeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterTargetMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterTargetMsg.h

## Purpose
Defines `RegisterTargetMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RegisterTarget`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RegisterTargetMsg` derives from `public NetMessageSerdes<RegisterTargetMsg>` and uses `BaseType(NETMSGTYPE_RegisterTarget)` or an equivalent base constructor. Constructors include `RegisterTargetMsg(const char* targetID, uint16_t targetNumID) : BaseType(NETMSGTYPE_RegisterTarget)`; `RegisterTargetMsg() : BaseType(NETMSGTYPE_RegisterTarget)`. Serialization writes `rawString(obj->targetID, obj->targetIDLen)`, `targetNumID`. Notable accessors/helpers include `getTargetID()`, `getTargetNumID()`. Declared payload/backing members include `unsigned targetIDLen`, `const char* targetID`, `uint16_t targetNumID`.

## Control Flow
Sender-side code builds `RegisterTargetMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/sock/NetworkInterfaceCard.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RegisterTarget`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RegisterTarget`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterTargetMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterTargetRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterTargetRespMsg.h

## Purpose
Defines `RegisterTargetRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_RegisterTargetResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RegisterTargetRespMsg` derives from `public SimpleUInt16Msg` and uses `BaseType(NETMSGTYPE_RegisterTargetResp)` or an equivalent base constructor. Constructors include `RegisterTargetRespMsg(uint16_t targetNumID) : SimpleUInt16Msg(NETMSGTYPE_RegisterTargetResp, targetNumID)`; `RegisterTargetRespMsg() : SimpleUInt16Msg(NETMSGTYPE_RegisterTargetResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getTargetNumID()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RegisterTargetRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `../SimpleUInt16Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RegisterTargetResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RegisterTargetResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterTargetRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveBuddyGroupMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveBuddyGroupMsg.h

## Purpose
Defines `RemoveBuddyGroupMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RemoveBuddyGroup`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveBuddyGroupMsg` derives from `public NetMessageSerdes<RemoveBuddyGroupMsg>` and uses `BaseType(NETMSGTYPE_RemoveBuddyGroup)` or an equivalent base constructor. Constructors include `RemoveBuddyGroupMsg(NodeType type, uint16_t groupID, bool checkOnly, bool force): BaseType(NETMSGTYPE_RemoveBuddyGroup), type(type), groupID(groupID), checkOnly(checkOnly), force(force)`; `RemoveBuddyGroupMsg() : BaseType(NETMSGTYPE_RemoveNode)`. Serialization writes `type`, `groupID`, `checkOnly`, `force`. Declared payload/backing members include `NodeType type`, `uint16_t groupID`, `bool checkOnly`, `bool force`.

## Control Flow
Sender-side code builds `RemoveBuddyGroupMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RemoveBuddyGroup`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveBuddyGroup`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveBuddyGroupMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveBuddyGroupRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveBuddyGroupRespMsg.h

## Purpose
Defines `RemoveBuddyGroupRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_RemoveBuddyGroupResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RemoveBuddyGroupRespMsg` derives from `public NetMessageSerdes<RemoveBuddyGroupRespMsg>` and uses `BaseType(NETMSGTYPE_RemoveBuddyGroupResp)` or an equivalent base constructor. Constructors include `RemoveBuddyGroupRespMsg(FhgfsOpsErr result): BaseType(NETMSGTYPE_RemoveBuddyGroupResp), result(result)`; `RemoveBuddyGroupRespMsg() : BaseType(NETMSGTYPE_RemoveBuddyGroupResp)`. Serialization writes `result`. Notable accessors/helpers include `getResult()`. Declared payload/backing members include `FhgfsOpsErr result`.

## Control Flow
Sender-side code builds `RemoveBuddyGroupRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RemoveBuddyGroupResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveBuddyGroupResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveBuddyGroupRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveNodeMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveNodeMsg.h

## Purpose
Defines `RemoveNodeMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RemoveNode`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveNodeMsg` derives from `public AcknowledgeableMsgSerdes<RemoveNodeMsg>` and uses `BaseType(NETMSGTYPE_RemoveNode)` or an equivalent base constructor. Constructors include `RemoveNodeMsg(NumNodeID nodeNumID, NodeType nodeType) : BaseType(NETMSGTYPE_RemoveNode)`; `RemoveNodeMsg() : BaseType(NETMSGTYPE_RemoveNode)`. Serialization writes `nodeType`, `nodeNumID`. Notable accessors/helpers include `serializeAckID()`, `getNodeNumID()`, `getNodeType()`. Declared payload/backing members include `NumNodeID nodeNumID`, `int16_t nodeType`.

## Control Flow
Sender-side code builds `RemoveNodeMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RemoveNode`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveNode`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveNodeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveNodeRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveNodeRespMsg.h

## Purpose
Defines `RemoveNodeRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_RemoveNodeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RemoveNodeRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RemoveNodeResp)` or an equivalent base constructor. Constructors include `RemoveNodeRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_RemoveNodeResp, result)`; `RemoveNodeRespMsg() : SimpleIntMsg(NETMSGTYPE_RemoveNodeResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RemoveNodeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RemoveNodeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveNodeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RemoveNodeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetMirrorBuddyGroupMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetMirrorBuddyGroupMsg.h

## Purpose
Defines `SetMirrorBuddyGroupMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_SetMirrorBuddyGroup`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetMirrorBuddyGroupMsg` derives from `public AcknowledgeableMsgSerdes<SetMirrorBuddyGroupMsg>` and uses `BaseType(NETMSGTYPE_SetMirrorBuddyGroup)` or an equivalent base constructor. Constructors include `SetMirrorBuddyGroupMsg(NodeType nodeType, uint16_t primaryTargetID, uint16_t secondaryTargetID, uint16_t buddyGroupID = 0, bool allowUpdate = false) : BaseType(NETMSGTYPE_SetMirrorBuddyGroup), nodeType(nodeType), primaryTargetID(primaryTargetID), secondaryTargetID(secondaryTargetID), buddyGroupID(buddyGroupID), allowUpdate(allowUpdate)`; `SetMirrorBuddyGroupMsg() : BaseType(NETMSGTYPE_SetMirrorBuddyGroup)`. Serialization writes `nodeType`, `primaryTargetID`, `secondaryTargetID`, `buddyGroupID`, `allowUpdate`. Notable accessors/helpers include `serializeAckID()`, `getNodeType()`, `getPrimaryTargetID()`, `getSecondaryTargetID()`, `getBuddyGroupID()`, `getAllowUpdate()`. Declared payload/backing members include `int32_t nodeType`, `uint16_t primaryTargetID`, `uint16_t secondaryTargetID`, `uint16_t buddyGroupID`, `bool allowUpdate`.

## Control Flow
Sender-side code builds `SetMirrorBuddyGroupMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_SetMirrorBuddyGroup`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetMirrorBuddyGroup`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetMirrorBuddyGroupMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetMirrorBuddyGroupRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetMirrorBuddyGroupRespMsg.h

## Purpose
Defines `SetMirrorBuddyGroupRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_SetMirrorBuddyGroupResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetMirrorBuddyGroupRespMsg` derives from `public NetMessageSerdes<SetMirrorBuddyGroupRespMsg>` and uses `BaseType(NETMSGTYPE_SetMirrorBuddyGroupResp)` or an equivalent base constructor. Constructors include `SetMirrorBuddyGroupRespMsg(FhgfsOpsErr result, uint16_t groupID = 0) : BaseType(NETMSGTYPE_SetMirrorBuddyGroupResp), result(result), groupID(groupID)`; `SetMirrorBuddyGroupRespMsg() : BaseType(NETMSGTYPE_SetMirrorBuddyGroupResp)`. Serialization writes `result`, `groupID`. Notable accessors/helpers include `getResult()`, `getBuddyGroupID()`. Declared payload/backing members include `FhgfsOpsErr result`, `uint16_t groupID`.

## Control Flow
Sender-side code builds `SetMirrorBuddyGroupRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_SetMirrorBuddyGroupResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetMirrorBuddyGroupResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetMirrorBuddyGroupRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetTargetConsistencyStatesMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetTargetConsistencyStatesMsg.h

## Purpose
Defines `SetTargetConsistencyStatesMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_SetTargetConsistencyStates`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetTargetConsistencyStatesMsg` derives from `public AcknowledgeableMsgSerdes<SetTargetConsistencyStatesMsg>` and uses `BaseType(NETMSGTYPE_SetTargetConsistencyStates)` or an equivalent base constructor. Constructors include `SetTargetConsistencyStatesMsg(NodeType nodeType, UInt16List* targetIDs, UInt8List* states, bool setOnline) : BaseType(NETMSGTYPE_SetTargetConsistencyStates)`; `SetTargetConsistencyStatesMsg() : BaseType(NETMSGTYPE_SetTargetConsistencyStates)`. Serialization writes `nodeType`, `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`, `backedPtr(obj->states, obj->parsed.states)`, `setOnline`. Notable accessors/helpers include `serializeAckID()`, `getNodeType()`, `getTargetIDs()`, `getStates()`, `getSetOnline()`. Declared payload/backing members include `int nodeType`, `UInt16List* targetIDs`, `UInt8List* states`, `bool setOnline`, `UInt16List targetIDs`, `UInt8List states`.

## Control Flow
Sender-side code builds `SetTargetConsistencyStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/nodes/Node.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_SetTargetConsistencyStates`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetTargetConsistencyStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetTargetConsistencyStatesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetTargetConsistencyStatesRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetTargetConsistencyStatesRespMsg.h

## Purpose
Defines `SetTargetConsistencyStatesRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_SetTargetConsistencyStatesResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetTargetConsistencyStatesRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_SetTargetConsistencyStatesResp)` or an equivalent base constructor. Constructors include `SetTargetConsistencyStatesRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_SetTargetConsistencyStatesResp, result)`; `SetTargetConsistencyStatesRespMsg() : SimpleIntMsg(NETMSGTYPE_SetTargetConsistencyStatesResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `SetTargetConsistencyStatesRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_SetTargetConsistencyStatesResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetTargetConsistencyStatesResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/SetTargetConsistencyStatesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsg.h

## Purpose
Defines `StorageBenchControlMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_StorageBenchControlMsg`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`StorageBenchControlMsg` derives from `public NetMessageSerdes<StorageBenchControlMsg>` and uses `BaseType(NETMSGTYPE_StorageBenchControlMsg)` or an equivalent base constructor. Constructors include `StorageBenchControlMsg(StorageBenchAction action, StorageBenchType type, int64_t blocksize, int64_t size, int threads, bool odirect, UInt16List* targetIDs) : BaseType(NETMSGTYPE_StorageBenchControlMsg)`; `StorageBenchControlMsg() : BaseType(NETMSGTYPE_StorageBenchControlMsg)`. Serialization writes `action`, `type`, `blocksize`, `size`, `threads`, `odirect`, `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`. Notable accessors/helpers include `getAction()`, `getType()`, `getBlocksize()`, `getSize()`, `getThreads()`, `getODirect()`, `getTargetIDs()`. Declared payload/backing members include `int32_t action`, `int32_t type`, `int64_t blocksize`, `int64_t size`, `int32_t threads`, `bool odirect`, `UInt16List* targetIDs`, `UInt16List targetIDs`.

## Control Flow
Sender-side code builds `StorageBenchControlMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/benchmark/StorageBench.h`, `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_StorageBenchControlMsg`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StorageBenchControlMsg`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsgResp.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsgResp.h

## Purpose
Defines `StorageBenchControlMsgResp`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_StorageBenchControlMsgResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`StorageBenchControlMsgResp` derives from `public NetMessageSerdes<StorageBenchControlMsgResp>` and uses `BaseType(NETMSGTYPE_StorageBenchControlMsgResp)` or an equivalent base constructor. Constructors include `StorageBenchControlMsgResp(StorageBenchStatus status, StorageBenchAction action, StorageBenchType type, int errorCode, StorageBenchResultsMap& results) : BaseType(NETMSGTYPE_StorageBenchControlMsgResp)`; `StorageBenchControlMsgResp() : BaseType(NETMSGTYPE_StorageBenchControlMsgResp)`. Serialization writes `status`, `action`, `type`, `errorCode`, `resultTargetIDs`, `resultValues`. Notable accessors/helpers include `getStatus()`, `getAction()`, `getType()`, `getErrorCode()`. Declared payload/backing members include `int32_t status`, `int32_t action`, `int32_t type`, `int32_t errorCode`, `UInt16List resultTargetIDs`, `Int64List resultValues`.

## Control Flow
Sender-side code builds `StorageBenchControlMsgResp` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/benchmark/StorageBench.h`, `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`, `common/toolkit/ZipIterator.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_StorageBenchControlMsgResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StorageBenchControlMsgResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsgResp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/UnmapTargetMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/UnmapTargetMsg.h

## Purpose
Defines `UnmapTargetMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_UnmapTarget`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UnmapTargetMsg` derives from `public SimpleUInt16Msg` and uses `BaseType(NETMSGTYPE_UnmapTarget)` or an equivalent base constructor. Constructors include `UnmapTargetMsg(uint16_t targetID) : SimpleUInt16Msg(NETMSGTYPE_UnmapTarget, targetID)`; `UnmapTargetMsg() : SimpleUInt16Msg(NETMSGTYPE_UnmapTarget)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getTargetID()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `UnmapTargetMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleUInt16Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_UnmapTarget`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnmapTarget`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/UnmapTargetMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/UnmapTargetRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/UnmapTargetRespMsg.h

## Purpose
Defines `UnmapTargetRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_UnmapTargetResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UnmapTargetRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_UnmapTargetResp)` or an equivalent base constructor. Constructors include `UnmapTargetRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_UnmapTargetResp, result)`; `UnmapTargetRespMsg() : SimpleIntMsg(NETMSGTYPE_UnmapTargetResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `UnmapTargetRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_UnmapTargetResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnmapTargetResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/UnmapTargetRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolMsg.h

## Purpose
Defines `AddStoragePoolMsg`, a BeeGFS storage pool management command message using `NETMSGTYPE_AddStoragePool`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`AddStoragePoolMsg` derives from `public NetMessageSerdes<AddStoragePoolMsg>` and uses `BaseType(NETMSGTYPE_AddStoragePool)` or an equivalent base constructor. Constructors include `AddStoragePoolMsg(StoragePoolId poolId, const std::string& description, const UInt16Set* targets, const UInt16Set* buddyGroups): BaseType(NETMSGTYPE_AddStoragePool), poolId(poolId), description(description), targetsPtr(targets), buddyGroupsPtr(buddyGroups)`; `AddStoragePoolMsg(): BaseType(NETMSGTYPE_AddStoragePool)`. Serialization writes `poolId`, `description`, `backedPtr(obj->targetsPtr, obj->targets)`, `backedPtr(obj->buddyGroupsPtr, obj->buddyGroups)`. Declared payload/backing members include `StoragePoolId poolId`, `std::string description`, `const UInt16Set* targetsPtr`, `UInt16Set targets`, `const UInt16Set* buddyGroupsPtr`, `UInt16Set buddyGroups`.

## Control Flow
Sender-side code builds `AddStoragePoolMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/storage/StoragePoolId.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_AddStoragePool`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_AddStoragePool`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolRespMsg.h

## Purpose
Defines `AddStoragePoolRespMsg`, the response payload wrapper for BeeGFS storage pool management RPCs using `NETMSGTYPE_AddStoragePoolResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`AddStoragePoolRespMsg` derives from `public NetMessageSerdes<AddStoragePoolRespMsg>` and uses `BaseType(NETMSGTYPE_AddStoragePoolResp)` or an equivalent base constructor. Constructors include `AddStoragePoolRespMsg(FhgfsOpsErr result, StoragePoolId poolId) : BaseType(NETMSGTYPE_AddStoragePoolResp), result(result), poolId(poolId)`; `AddStoragePoolRespMsg() : BaseType(NETMSGTYPE_AddStoragePoolResp)`. Serialization writes `result`, `poolId`. Notable accessors/helpers include `getResult()`, `getPoolId()`. Declared payload/backing members include `FhgfsOpsErr result`, `StoragePoolId poolId`.

## Control Flow
Sender-side code builds `AddStoragePoolRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageErrors.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_AddStoragePoolResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_AddStoragePoolResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/AddStoragePoolRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/GetStoragePoolsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/GetStoragePoolsMsg.h

## Purpose
Defines `GetStoragePoolsMsg`, a BeeGFS storage pool management query/request message using `NETMSGTYPE_GetStoragePools`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetStoragePoolsMsg` derives from `public SimpleMsg` and uses `BaseType(NETMSGTYPE_GetStoragePools)` or an equivalent base constructor. Constructors include `GetStoragePoolsMsg(): SimpleMsg(NETMSGTYPE_GetStoragePools)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetStoragePoolsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_GetStoragePools`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetStoragePools`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/GetStoragePoolsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/GetStoragePoolsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/GetStoragePoolsRespMsg.h

## Purpose
Defines `GetStoragePoolsRespMsg`, the response payload wrapper for BeeGFS storage pool management RPCs using `NETMSGTYPE_GetStoragePoolsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetStoragePoolsRespMsg` derives from `public NetMessageSerdes<GetStoragePoolsRespMsg>` and uses `BaseType(NETMSGTYPE_GetStoragePoolsResp)` or an equivalent base constructor. Constructors include `GetStoragePoolsRespMsg(StoragePoolPtrVec* pools): BaseType(NETMSGTYPE_GetStoragePoolsResp), pools(pools)`; `GetStoragePoolsRespMsg(): BaseType(NETMSGTYPE_GetStoragePoolsResp)`. Serialization writes `backedPtr(obj->pools, obj->parsed.pools)`. Notable accessors/helpers include `getStoragePools()`. Declared payload/backing members include `StoragePoolPtrVec* pools`, `StoragePoolPtrVec pools`.

## Control Flow
Sender-side code builds `GetStoragePoolsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StoragePool.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_GetStoragePoolsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetStoragePoolsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/GetStoragePoolsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/ModifyStoragePoolMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/ModifyStoragePoolMsg.h

## Purpose
Defines `ModifyStoragePoolMsg`, a BeeGFS storage pool management command message using `NETMSGTYPE_ModifyStoragePool`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ModifyStoragePoolMsg` derives from `public NetMessageSerdes<ModifyStoragePoolMsg>` and uses `BaseType(NETMSGTYPE_ModifyStoragePool)` or an equivalent base constructor. Constructors include `ModifyStoragePoolMsg(StoragePoolId poolId, const UInt16Vector* addTargets, const UInt16Vector* rmTargets, const UInt16Vector* addBuddyGroups, const UInt16Vector* rmBuddyGroups, const std::string* newDescription) : BaseType(NETMSGTYPE_ModifyStoragePool), poolId(poolId), addTargets(addTargets), rmTargets(rmTargets), addBuddyGroups(addBuddyGroups), rmBuddyGroups(rmBuddyGroups), newDescription(newDescription)`; `ModifyStoragePoolMsg(): BaseType(NETMSGTYPE_ModifyStoragePool), addTargets(nullptr), rmTargets(nullptr), addBuddyGroups(nullptr), rmBuddyGroups(nullptr), newDescription(nullptr)`. Serialization writes `poolId`, `backedPtr(obj->newDescription, obj->parsed.newDescription)`, `backedPtr(obj->addTargets, obj->parsed.addTargets)`, `backedPtr(obj->rmTargets, obj->parsed.rmTargets)`, `backedPtr(obj->addBuddyGroups, obj->parsed.addBuddyGroups)`, `backedPtr(obj->rmBuddyGroups, obj->parsed.rmBuddyGroups)`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `static const unsigned HAS_NEWDESCRIPTION`, `static const unsigned HAS_ADDTARGETS`, `static const unsigned HAS_RMTARGETS`, `static const unsigned HAS_ADDBUDDYGROUPS`, `static const unsigned HAS_RMBUDDYGROUPS`, `StoragePoolId poolId`, `const UInt16Vector* addTargets`, `const UInt16Vector* rmTargets`, `const UInt16Vector* addBuddyGroups`, `const UInt16Vector* rmBuddyGroups`, `const std::string* newDescription`, `UInt16Vector addTargets`, `UInt16Vector rmTargets`, `UInt16Vector addBuddyGroups`, plus additional backing fields.

## Control Flow
Sender-side code builds `ModifyStoragePoolMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_ModifyStoragePool`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ModifyStoragePool`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/ModifyStoragePoolMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/ModifyStoragePoolRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/ModifyStoragePoolRespMsg.h

## Purpose
Defines `ModifyStoragePoolRespMsg`, the response payload wrapper for BeeGFS storage pool management RPCs using `NETMSGTYPE_ModifyStoragePoolResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`ModifyStoragePoolRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_ModifyStoragePoolResp)` or an equivalent base constructor. Constructors include `ModifyStoragePoolRespMsg(FhgfsOpsErr result): SimpleIntMsg(NETMSGTYPE_ModifyStoragePoolResp, result)`; `ModifyStoragePoolRespMsg() : SimpleIntMsg(NETMSGTYPE_ModifyStoragePoolResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `ModifyStoragePoolRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_ModifyStoragePoolResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ModifyStoragePoolResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/ModifyStoragePoolRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RefreshStoragePoolsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RefreshStoragePoolsMsg.h

## Purpose
Defines `RefreshStoragePoolsMsg`, a BeeGFS storage pool management command message using `NETMSGTYPE_RefreshStoragePools`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RefreshStoragePoolsMsg` derives from `public AcknowledgeableMsgSerdes<RefreshStoragePoolsMsg>` and uses `BaseType(NETMSGTYPE_RefreshStoragePools)` or an equivalent base constructor. Constructors include `RefreshStoragePoolsMsg(): BaseType(NETMSGTYPE_RefreshStoragePools)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `serializeAckID()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RefreshStoragePoolsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_RefreshStoragePools`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshStoragePools`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RefreshStoragePoolsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RemoveStoragePoolMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RemoveStoragePoolMsg.h

## Purpose
Defines `RemoveStoragePoolMsg`, a BeeGFS storage pool management command message using `NETMSGTYPE_RemoveStoragePool`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveStoragePoolMsg` derives from `public NetMessageSerdes<RemoveStoragePoolMsg>` and uses `BaseType(NETMSGTYPE_RemoveStoragePool)` or an equivalent base constructor. Constructors include `RemoveStoragePoolMsg(StoragePoolId poolId) : BaseType(NETMSGTYPE_RemoveStoragePool), poolId(poolId)`; `RemoveStoragePoolMsg() : BaseType(NETMSGTYPE_RemoveStoragePool)`. Serialization writes `poolId`. Declared payload/backing members include `StoragePoolId poolId`.

## Control Flow
Sender-side code builds `RemoveStoragePoolMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StoragePoolId.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_RemoveStoragePool`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveStoragePool`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RemoveStoragePoolMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RemoveStoragePoolRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RemoveStoragePoolRespMsg.h

## Purpose
Defines `RemoveStoragePoolRespMsg`, the response payload wrapper for BeeGFS storage pool management RPCs using `NETMSGTYPE_RemoveStoragePoolResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RemoveStoragePoolRespMsg` derives from `public NetMessageSerdes<RemoveStoragePoolRespMsg>` and uses `BaseType(NETMSGTYPE_RemoveStoragePoolResp)` or an equivalent base constructor. Constructors include `RemoveStoragePoolRespMsg(FhgfsOpsErr result): BaseType(NETMSGTYPE_RemoveStoragePoolResp), result(result)`; `RemoveStoragePoolRespMsg() : BaseType(NETMSGTYPE_RemoveStoragePoolResp)`. Serialization writes `result`. Notable accessors/helpers include `getResult()`. Declared payload/backing members include `FhgfsOpsErr result`.

## Control Flow
Sender-side code builds `RemoveStoragePoolRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage pool management code path that handles `NETMSGTYPE_RemoveStoragePoolResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveStoragePoolResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/nodes/storagepools/RemoveStoragePoolRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/AckNotifyMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/AckNotifyMsg.h

## Purpose
Defines `AckNotifiyMsg`, a BeeGFS session lifecycle command message using `NETMSGTYPE_AckNotify`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`AckNotifiyMsg` derives from `public MirroredMessageBase<AckNotifiyMsg>` and uses `BaseType(NETMSGTYPE_AckNotify)` or an equivalent base constructor. Constructors include `AckNotifiyMsg(): BaseType(NETMSGTYPE_AckNotify)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `supportsMirroring()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `AckNotifiyMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_AckNotify`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_AckNotify`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/AckNotifyMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/AckNotifyRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/AckNotifyRespMsg.h

## Purpose
Defines `AckNotifiyRespMsg`, the response payload wrapper for BeeGFS session lifecycle RPCs using `NETMSGTYPE_AckNotifyResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`AckNotifiyRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_AckNotifyResp)` or an equivalent base constructor. Constructors include `AckNotifiyRespMsg(FhgfsOpsErr result): SimpleIntMsg(NETMSGTYPE_AckNotifyResp, result)`; `AckNotifiyRespMsg(): SimpleIntMsg(NETMSGTYPE_AckNotifyResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `AckNotifiyRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_AckNotifyResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_AckNotifyResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/AckNotifyRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/BumpFileVersionMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/BumpFileVersionMsg.h

## Purpose
Defines `BumpFileVersionMsg`, a BeeGFS session lifecycle command message using `NETMSGTYPE_BumpFileVersion`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`BumpFileVersionMsg` derives from `public MirroredMessageBase<BumpFileVersionMsg>` and uses `BaseType(NETMSGTYPE_BumpFileVersion)` or an equivalent base constructor. Constructors include `BumpFileVersionMsg(EntryInfo& entryInfo) : BaseType(NETMSGTYPE_BumpFileVersion), entryInfo(&entryInfo)`; `BumpFileVersionMsg() : BaseType(NETMSGTYPE_BumpFileVersion)`. Serialization writes `backedPtr(obj->entryInfo, obj->parsed.entryInfo)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getSupportedHeaderFeatureFlagsMask()`, `getEntryInfo()`, `getFileEvent()`. Declared payload/backing members include `EntryInfo* entryInfo`, `FileEvent fileEvent`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `BumpFileVersionMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_BumpFileVersion`. Feature flags: `BUMPFILEVERSIONMSG_FLAG_PERSISTENT`=1, `BUMPFILEVERSIONMSG_FLAG_HASEVENT`=2. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_BumpFileVersion`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/BumpFileVersionMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/BumpFileVersionRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/BumpFileVersionRespMsg.h

## Purpose
Defines `BumpFileVersionRespMsg`, the response payload wrapper for BeeGFS session lifecycle RPCs using `NETMSGTYPE_BumpFileVersionResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`BumpFileVersionRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_BumpFileVersionResp)` or an equivalent base constructor. Constructors include `BumpFileVersionRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_BumpFileVersionResp, result)`; `BumpFileVersionRespMsg() : SimpleIntMsg(NETMSGTYPE_BumpFileVersionResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `BumpFileVersionRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `../SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_BumpFileVersionResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_BumpFileVersionResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/BumpFileVersionRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileMsg.h

## Purpose
Defines `FSyncLocalFileMsg`, a BeeGFS session lifecycle command message using `NETMSGTYPE_FSyncLocalFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`FSyncLocalFileMsg` derives from `public NetMessageSerdes<FSyncLocalFileMsg>` and uses `BaseType(NETMSGTYPE_FSyncLocalFile)` or an equivalent base constructor. Constructors include `FSyncLocalFileMsg(const NumNodeID sessionID, const char* fileHandleID, const uint16_t targetID) : BaseType(NETMSGTYPE_FSyncLocalFile)`; `FSyncLocalFileMsg() : BaseType(NETMSGTYPE_FSyncLocalFile)`. Serialization writes `sessionID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getSessionID()`, `getFileHandleID()`, `getTargetID()`. Declared payload/backing members include `NumNodeID sessionID`, `const char* fileHandleID`, `unsigned fileHandleIDLen`, `uint16_t targetID`.

## Control Flow
Sender-side code builds `FSyncLocalFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_FSyncLocalFile`. Feature flags: `FSYNCLOCALFILEMSG_FLAG_NO_SYNC`=1, `FSYNCLOCALFILEMSG_FLAG_SESSION_CHECK`=2, `FSYNCLOCALFILEMSG_FLAG_BUDDYMIRROR`=4, `FSYNCLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FSyncLocalFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileRespMsg.h

## Purpose
Defines `FSyncLocalFileRespMsg`, the response payload wrapper for BeeGFS session lifecycle RPCs using `NETMSGTYPE_FSyncLocalFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`FSyncLocalFileRespMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_FSyncLocalFileResp)` or an equivalent base constructor. Constructors include `FSyncLocalFileRespMsg(int64_t result) : SimpleInt64Msg(NETMSGTYPE_FSyncLocalFileResp, result)`; `FSyncLocalFileRespMsg() : SimpleInt64Msg(NETMSGTYPE_FSyncLocalFileResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `FSyncLocalFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `../SimpleInt64Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_FSyncLocalFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FSyncLocalFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/GetFileVersionMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/GetFileVersionMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/GetFileVersionRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/GetFileVersionRespMsg.h

## Purpose
Defines `GetFileVersionRespMsg`, the response payload wrapper for BeeGFS session lifecycle RPCs using `NETMSGTYPE_GetFileVersionResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetFileVersionRespMsg` derives from `public NetMessageSerdes<GetFileVersionRespMsg>` and uses `BaseType(NETMSGTYPE_GetFileVersionResp)` or an equivalent base constructor. Constructors include `GetFileVersionRespMsg(FhgfsOpsErr result, uint32_t version) : BaseType(NETMSGTYPE_GetFileVersionResp), result(result), version(version)`; `GetFileVersionRespMsg() : BaseType(NETMSGTYPE_GetFileVersionResp)`. Serialization writes `result`, `version`. Notable accessors/helpers include `getVersion()`. Declared payload/backing members include `FhgfsOpsErr result`, `uint32_t version`.

## Control Flow
Sender-side code builds `GetFileVersionRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_GetFileVersionResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetFileVersionResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/GetFileVersionRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/RefreshSessionMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/RefreshSessionMsg.h

## Purpose
Defines `RefreshSessionMsg`, a BeeGFS session lifecycle command message using `NETMSGTYPE_RefreshSession`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RefreshSessionMsg` derives from `public NetMessageSerdes<RefreshSessionMsg>` and uses `BaseType(NETMSGTYPE_RefreshSession)` or an equivalent base constructor. Constructors include `RefreshSessionMsg(const char* sessionID) : BaseType(NETMSGTYPE_RefreshSession)`; `RefreshSessionMsg() : BaseType(NETMSGTYPE_RefreshSession)`. Serialization writes `rawString(obj->sessionID, obj->sessionIDLen)`. Notable accessors/helpers include `getSessionID()`. Declared payload/backing members include `unsigned sessionIDLen`, `const char* sessionID`.

## Control Flow
Sender-side code builds `RefreshSessionMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_RefreshSession`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshSession`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/RefreshSessionMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/RefreshSessionRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/RefreshSessionRespMsg.h

## Purpose
Defines `RefreshSessionRespMsg`, the response payload wrapper for BeeGFS session lifecycle RPCs using `NETMSGTYPE_RefreshSessionResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RefreshSessionRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RefreshSessionResp)` or an equivalent base constructor. Constructors include `RefreshSessionRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_RefreshSessionResp, result)`; `RefreshSessionRespMsg() : SimpleIntMsg(NETMSGTYPE_RefreshSessionResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RefreshSessionRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_RefreshSessionResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshSessionResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/RefreshSessionRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockAppendMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockAppendMsg.h

## Purpose
Defines `FLockAppendMsg`, a BeeGFS session locking command message using `NETMSGTYPE_FLockAppend`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`FLockAppendMsg` derives from `public MirroredMessageBase<FLockAppendMsg>` and uses `BaseType(NETMSGTYPE_FLockAppend)` or an equivalent base constructor. Constructors include `FLockAppendMsg(const NumNodeID clientNumID, const char* fileHandleID, const int64_t clientFD, const int ownerPID, const int lockTypeFlags, const char* lockAckID) : BaseType(NETMSGTYPE_FLockAppend)`; `FLockAppendMsg() : BaseType(NETMSGTYPE_FLockAppend)`. Serialization writes `clientNumID`, `clientFD`, `ownerPID`, `lockTypeFlags`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `rawString(obj->lockAckID, obj->lockAckIDLen, 4)`. Notable accessors/helpers include `supportsMirroring()`, `getClientNumID()`, `getFileHandleID()`, `getClientFD()`, `getOwnerPID()`, `getLockTypeFlags()`, `getLockAckID()`, `getEntryInfo()`. Declared payload/backing members include `NumNodeID clientNumID`, `const char* fileHandleID`, `unsigned fileHandleIDLen`, `int64_t clientFD`, `int32_t lockTypeFlags`, `const char* lockAckID`, `unsigned lockAckIDLen`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `FLockAppendMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_FLockAppend`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FLockAppend`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockAppendMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockAppendRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockAppendRespMsg.h

## Purpose
Defines `FLockAppendRespMsg`, the response payload wrapper for BeeGFS session locking RPCs using `NETMSGTYPE_FLockAppendResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`FLockAppendRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_FLockAppendResp)` or an equivalent base constructor. Constructors include `FLockAppendRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_FLockAppendResp, result)`; `FLockAppendRespMsg() : SimpleIntMsg(NETMSGTYPE_FLockAppendResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `FLockAppendRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_FLockAppendResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FLockAppendResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockAppendRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockEntryMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockEntryMsg.h

## Purpose
Defines `FLockEntryMsg`, a BeeGFS session locking command message using `NETMSGTYPE_FLockEntry`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`FLockEntryMsg` derives from `public MirroredMessageBase<FLockEntryMsg>` and uses `BaseType(NETMSGTYPE_FLockEntry)` or an equivalent base constructor. Constructors include `FLockEntryMsg(const NumNodeID clientNumID, const char* fileHandleID, const int64_t clientFD, const int ownerPID, const int lockTypeFlags, const char* lockAckID) : BaseType(NETMSGTYPE_FLockEntry)`; `FLockEntryMsg() : BaseType(NETMSGTYPE_FLockEntry)`. Serialization writes `clientNumID`, `clientFD`, `ownerPID`, `lockTypeFlags`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `rawString(obj->lockAckID, obj->lockAckIDLen, 4)`. Notable accessors/helpers include `supportsMirroring()`, `getClientNumID()`, `getFileHandleID()`, `getClientFD()`, `getOwnerPID()`, `getLockTypeFlags()`, `getLockAckID()`, `getEntryInfo()`. Declared payload/backing members include `NumNodeID clientNumID`, `const char* fileHandleID`, `unsigned fileHandleIDLen`, `int64_t clientFD`, `int32_t lockTypeFlags`, `const char* lockAckID`, `unsigned lockAckIDLen`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `FLockEntryMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_FLockEntry`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FLockEntry`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockEntryMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockEntryRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockEntryRespMsg.h

## Purpose
Defines `FLockEntryRespMsg`, the response payload wrapper for BeeGFS session locking RPCs using `NETMSGTYPE_FLockEntryResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`FLockEntryRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_FLockEntryResp)` or an equivalent base constructor. Constructors include `FLockEntryRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_FLockEntryResp, result)`; `FLockEntryRespMsg() : SimpleIntMsg(NETMSGTYPE_FLockEntryResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `FLockEntryRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_FLockEntryResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FLockEntryResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockEntryRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockRangeMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockRangeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockRangeRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockRangeRespMsg.h

## Purpose
Defines `FLockRangeRespMsg`, the response payload wrapper for BeeGFS session locking RPCs using `NETMSGTYPE_FLockRangeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`FLockRangeRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_FLockRangeResp)` or an equivalent base constructor. Constructors include `FLockRangeRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_FLockRangeResp, result)`; `FLockRangeRespMsg() : SimpleIntMsg(NETMSGTYPE_FLockRangeResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `FLockRangeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_FLockRangeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FLockRangeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/FLockRangeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/LockGrantedMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/LockGrantedMsg.h

## Purpose
Defines `LockGrantedMsg`, a BeeGFS session locking command message using `NETMSGTYPE_LockGranted`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`LockGrantedMsg` derives from `public AcknowledgeableMsgSerdes<LockGrantedMsg>` and uses `BaseType(NETMSGTYPE_LockGranted)` or an equivalent base constructor. Constructors include `LockGrantedMsg(const std::string& lockAckID, const std::string& ackID, NumNodeID granterNodeID) : BaseType(NETMSGTYPE_LockGranted, ackID.c_str())`; `LockGrantedMsg() : BaseType(NETMSGTYPE_LockGranted)`. Serialization writes `rawString(obj->lockAckID, obj->lockAckIDLen, 4)`, `granterNodeID`. Notable accessors/helpers include `serializeAckID()`, `getLockAckID()`, `getGranterNodeID()`. Declared payload/backing members include `unsigned lockAckIDLen`, `const char* lockAckID`, `NumNodeID granterNodeID`.

## Control Flow
Sender-side code builds `LockGrantedMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/nodes/NumNodeID.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_LockGranted`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_LockGranted`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/LockGrantedMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileMsg.h

## Purpose
Defines `CloseChunkFileMsg`, a BeeGFS file open and close session command message using `NETMSGTYPE_CloseChunkFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`CloseChunkFileMsg` derives from `public NetMessageSerdes<CloseChunkFileMsg>` and uses `BaseType(NETMSGTYPE_CloseChunkFile)` or an equivalent base constructor. Constructors include `CloseChunkFileMsg(const NumNodeID sessionID, const std::string& fileHandleID, const uint16_t targetID, const PathInfo* pathInfo) : BaseType(NETMSGTYPE_CloseChunkFile)`; `CloseChunkFileMsg() : BaseType(NETMSGTYPE_CloseChunkFile)`. Serialization writes `sessionID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getSessionID()`, `getFileHandleID()`, `getTargetID()`, `getPathInfo()`. Declared payload/backing members include `NumNodeID sessionID`, `unsigned fileHandleIDLen`, `const char* fileHandleID`, `uint16_t targetID`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `CloseChunkFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_CloseChunkFile`. Feature flags: `CLOSECHUNKFILEMSG_FLAG_NODYNAMICATTRIBS`=1, `CLOSECHUNKFILEMSG_FLAG_BUDDYMIRROR`=4, `CLOSECHUNKFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CloseChunkFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileRespMsg.h

## Purpose
Defines `CloseChunkFileRespMsg`, the response payload wrapper for BeeGFS file open and close session RPCs using `NETMSGTYPE_CloseChunkFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`CloseChunkFileRespMsg` derives from `public NetMessageSerdes<CloseChunkFileRespMsg>` and uses `BaseType(NETMSGTYPE_CloseChunkFileResp)` or an equivalent base constructor. Constructors include `CloseChunkFileRespMsg(FhgfsOpsErr result, int64_t filesize, int64_t allocedBlocks, int64_t modificationTimeSecs, int64_t lastAccessTimeSecs, uint64_t storageVersion) : BaseType(NETMSGTYPE_CloseChunkFileResp)`; `CloseChunkFileRespMsg() : BaseType(NETMSGTYPE_CloseChunkFileResp)`. Serialization writes `filesize`, `allocedBlocks`, `modificationTimeSecs`, `lastAccessTimeSecs`, `storageVersion`, `result`. Notable accessors/helpers include `getResult()`, `getFileSize()`, `getAllocedBlocks()`, `getModificationTimeSecs()`, `getLastAccessTimeSecs()`, `getStorageVersion()`. Declared payload/backing members include `int32_t result`, `int64_t filesize`, `int64_t modificationTimeSecs`, `int64_t lastAccessTimeSecs`, `uint64_t storageVersion`.

## Control Flow
Sender-side code builds `CloseChunkFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_CloseChunkFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CloseChunkFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseChunkFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseFileMsg.h

## Purpose
Defines `CloseFileMsg`, a BeeGFS file open and close session command message using `NETMSGTYPE_CloseFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`CloseFileMsg` derives from `public MirroredMessageBase<CloseFileMsg>` and uses `BaseType(NETMSGTYPE_CloseFile)` or an equivalent base constructor. Constructors include `CloseFileMsg(const NumNodeID clientNumID, const std::string& fileHandleID, EntryInfo* entryInfo, const int maxUsedNodeIndex) : BaseType(NETMSGTYPE_CloseFile)`; `CloseFileMsg() : BaseType(NETMSGTYPE_CloseFile)`. Serialization writes `clientNumID`, `stringAlign4(obj->fileHandleID)`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `maxUsedNodeIndex`, `dynAttribs`, `inodeTimestamps`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `supportsMirroring()`, `getClientNumID()`, `getFileHandleID()`, `getMaxUsedNodeIndex()`, `getEntryInfo()`, `getFileEvent()`. Declared payload/backing members include `NumNodeID clientNumID`, `std::string fileHandleID`, `int32_t maxUsedNodeIndex`, `FileEvent fileEvent`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `DynamicFileAttribsVec dynAttribs`, `MirroredTimestamps inodeTimestamps`.

## Control Flow
Sender-side code builds `CloseFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/StatData.h`, `common/storage/striping/DynamicFileAttribs.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_CloseFile`. Feature flags: `CLOSEFILEMSG_FLAG_EARLYRESPONSE`=1, `CLOSEFILEMSG_FLAG_CANCELAPPENDLOCKS`=2, `CLOSEFILEMSG_FLAG_DYNATTRIBS`=4, `CLOSEFILEMSG_FLAG_HAS_EVENT`=8. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CloseFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseFileRespMsg.h

## Purpose
Defines `CloseFileRespMsg`, the response payload wrapper for BeeGFS file open and close session RPCs using `NETMSGTYPE_CloseFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`CloseFileRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_CloseFileResp)` or an equivalent base constructor. Constructors include `CloseFileRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_CloseFileResp, result)`; `CloseFileRespMsg() : SimpleIntMsg(NETMSGTYPE_CloseFileResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `CloseFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_CloseFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CloseFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/CloseFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/OpenFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/OpenFileMsg.h

## Purpose
Defines `OpenFileMsg`, a BeeGFS file open and close session command message using `NETMSGTYPE_OpenFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`OpenFileMsg` derives from `public MirroredMessageBase<OpenFileMsg>` and uses `BaseType(NETMSGTYPE_OpenFile)` or an equivalent base constructor. Constructors include `OpenFileMsg(const NumNodeID clientNumID, const EntryInfo* entryInfo, const unsigned accessFlags) : BaseType(NETMSGTYPE_OpenFile), clientNumID(clientNumID), accessFlags(accessFlags), entryInfoPtr(entryInfo)`; `OpenFileMsg() : BaseType(NETMSGTYPE_OpenFile)`. Serialization writes `clientNumID`, `accessFlags`, `sessionFileID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `fileTimestamps`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getClientNumID()`, `getEntryInfo()`, `getAccessFlags()`, `getSupportedHeaderFeatureFlagsMask()`, `supportsMirroring()`, `getFileHandleID()`, `setFileHandleID()`, `getSessionFileID()`, `setSessionFileID()`, `getFileEvent()`. Declared payload/backing members include `NumNodeID clientNumID`, `uint32_t accessFlags`, `uint32_t sessionFileID`, `const char* fileHandleID`, `unsigned fileHandleIDLen`, `FileEvent fileEvent`, `const EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `MirroredTimestamps fileTimestamps`.

## Control Flow
Sender-side code builds `OpenFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_OpenFile`. Feature flags: `OPENFILEMSG_FLAG_USE_QUOTA`=1, `OPENFILEMSG_FLAG_HAS_EVENT`=2, `OPENFILEMSG_FLAG_BYPASS_ACCESS_CHECK`=4. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_OpenFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/OpenFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/OpenFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/OpenFileRespMsg.h

## Purpose
Defines `OpenFileRespMsg`, the response payload wrapper for BeeGFS file open and close session RPCs using `NETMSGTYPE_OpenFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`OpenFileRespMsg` derives from `public NetMessageSerdes<OpenFileRespMsg>` and uses `BaseType(NETMSGTYPE_OpenFileResp)` or an equivalent base constructor. Constructors include `OpenFileRespMsg(int result, const char* fileHandleID, StripePattern* pattern, PathInfo* pathInfo, uint32_t fileVersion = 0, uint8_t fileStateRaw = 0) : BaseType(NETMSGTYPE_OpenFileResp), fileVersion(fileVersion), fileStateRaw(fileStateRaw)`; `OpenFileRespMsg(int result, std::string& fileHandleID, StripePattern* pattern, PathInfo* pathInfo, uint32_t fileVersion, uint8_t fileStateRaw = 0) : BaseType(NETMSGTYPE_OpenFileResp), fileVersion(fileVersion), fileStateRaw(fileStateRaw)`; `OpenFileRespMsg() : BaseType(NETMSGTYPE_OpenFileResp)`. Serialization writes `result`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `pathInfo`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `fileVersion`, `isMsgHeaderCompatFeatureFlagSet`, `fileStateRaw`. Notable accessors/helpers include `set()`, `isMsgHeaderCompatFeatureFlagSet()`, `getPattern()`, `getResult()`, `getFileHandleID()`, `getPathInfo()`. Declared payload/backing members include `int32_t result`, `unsigned fileHandleIDLen`, `const char* fileHandleID`, `PathInfo pathInfo`, `uint32_t fileVersion`, `StripePattern* pattern`, `std::unique_ptr<StripePattern> pattern`, `uint8_t fileStateRaw`.

## Control Flow
Sender-side code builds `OpenFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/StripePattern.h`, `common/storage/PathInfo.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the file open and close session code path that handles `NETMSGTYPE_OpenFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_OpenFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/opening/OpenFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.h

## Purpose
Defines `ReadLocalFileRDMAMsg`, a BeeGFS storage I/O session command message using `NETMSGTYPE_ReadLocalFileRDMA`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ReadLocalFileRDMAMsg` derives from `public ReadLocalFileV2MsgBase, public NetMessageSerdes<ReadLocalFileRDMAMsg>` and uses `BaseType(NETMSGTYPE_ReadLocalFileRDMA)` or an equivalent base constructor. Constructors include `ReadLocalFileRDMAMsg(NumNodeID clientNumID, const char* fileHandleID, uint16_t targetID, PathInfo* pathInfoPtr, unsigned accessFlags, int64_t offset, int64_t count) : ReadLocalFileV2MsgBase(clientNumID, fileHandleID, targetID, pathInfoPtr, accessFlags, offset, count), BaseType(NETMSGTYPE_ReadLocalFileRDMA)`; `ReadLocalFileRDMAMsg() : ReadLocalFileV2MsgBase(), BaseType(NETMSGTYPE_ReadLocalFileRDMA)`. Serialization writes `rdmaInfo`. Notable accessors/helpers include `getRdmaInfo()`, `getSupportedHeaderFeatureFlagsMask()`, `isMsgValid()`, `isValid()`. Declared payload/backing members include `RdmaInfo rdmaInfo`.

## Control Flow
Sender-side code builds `ReadLocalFileRDMAMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`, `common/storage/RdmaInfo.h`, `common/app/log/LogContext.h`, `common/net/message/session/rw/ReadLocalFileV2Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_ReadLocalFileRDMA`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
I/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ReadLocalFileRDMA`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior. Validate control-message fields together with data-transfer or RDMA descriptor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileV2Msg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileV2Msg.h

## Purpose
Defines `ReadLocalFileV2Msg`, a BeeGFS storage I/O session command message using `NETMSGTYPE_ReadLocalFileV2`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`ReadLocalFileV2Msg` derives from `public ReadLocalFileV2MsgBase, public NetMessageSerdes<ReadLocalFileV2Msg>` and uses `BaseType(NETMSGTYPE_ReadLocalFileV2)` or an equivalent base constructor. Constructors include `ReadLocalFileV2Msg(NumNodeID clientNumID, const char* fileHandleID, uint16_t targetID, PathInfo* pathInfoPtr, unsigned accessFlags, int64_t offset, int64_t count) : ReadLocalFileV2MsgBase(clientNumID, fileHandleID, targetID, pathInfoPtr, accessFlags, offset, count), BaseType(NETMSGTYPE_ReadLocalFileV2)`; `ReadLocalFileV2Msg() : ReadLocalFileV2MsgBase(), BaseType(NETMSGTYPE_ReadLocalFileV2)`. Serialization writes `offset`, `count`, `accessFlags`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `clientNumID`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `ReadLocalFileV2Msg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_ReadLocalFileV2`. Feature flags: `READLOCALFILEMSG_FLAG_SESSION_CHECK`=1, `READLOCALFILEMSG_FLAG_DISABLE_IO`=2, `READLOCALFILEMSG_FLAG_BUDDYMIRROR`=4, `READLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; offset cursors can repeat or skip records if callers mishandle continuation; i/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ReadLocalFileV2`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior. Validate control-message fields together with data-transfer or RDMA descriptor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/ReadLocalFileV2Msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileMsg.h

## Purpose
Defines `WriteLocalFileMsg`, a BeeGFS storage I/O session command message using `NETMSGTYPE_WriteLocalFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`WriteLocalFileMsg` derives from `public WriteLocalFileMsgBase, public NetMessageSerdes<WriteLocalFileMsg>` and uses `BaseType(NETMSGTYPE_WriteLocalFile)` or an equivalent base constructor. Constructors include `WriteLocalFileMsg(const NumNodeID clientNumID, const char* fileHandleID, const uint16_t targetID, const PathInfo* pathInfo, const unsigned accessFlags, const int64_t offset, const int64_t count) : WriteLocalFileMsgBase(clientNumID, fileHandleID, targetID, pathInfo, accessFlags, offset, count), BaseType(NETMSGTYPE_WriteLocalFile)`; `WriteLocalFileMsg() : WriteLocalFileMsgBase(), BaseType(NETMSGTYPE_WriteLocalFile)`. Serialization writes `offset`, `count`, `accessFlags`, `userID`, `groupID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `clientNumID`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `setUserdataForQuota()`, `getSupportedHeaderFeatureFlagsMask()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `WriteLocalFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_WriteLocalFile`. Feature flags: `WRITELOCALFILEMSG_FLAG_SESSION_CHECK`=1, `WRITELOCALFILEMSG_FLAG_USE_QUOTA`=2, `WRITELOCALFILEMSG_FLAG_DISABLE_IO`=4, `WRITELOCALFILEMSG_FLAG_BUDDYMIRROR`=8, `WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=16, `WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_FORWARD`=32.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; offset cursors can repeat or skip records if callers mishandle continuation; i/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_WriteLocalFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior. Validate control-message fields together with data-transfer or RDMA descriptor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.h

## Purpose
Defines `WriteLocalFileRDMAMsg`, a BeeGFS storage I/O session command message using `NETMSGTYPE_WriteLocalFileRDMA`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`WriteLocalFileRDMAMsg` derives from `public WriteLocalFileMsgBase, public NetMessageSerdes<WriteLocalFileRDMAMsg>` and uses `BaseType(NETMSGTYPE_WriteLocalFileRDMA)` or an equivalent base constructor. Constructors include `WriteLocalFileRDMAMsg(const NumNodeID clientNumID, const char* fileHandleID, const uint16_t targetID, const PathInfo* pathInfo, const unsigned accessFlags, const int64_t offset, const int64_t count) : WriteLocalFileMsgBase(clientNumID, fileHandleID, targetID, pathInfo, accessFlags, offset, count), BaseType(NETMSGTYPE_WriteLocalFileRDMA)`; `WriteLocalFileRDMAMsg() : WriteLocalFileMsgBase(), BaseType(NETMSGTYPE_WriteLocalFileRDMA)`. Serialization writes `rdmaInfo`. Notable accessors/helpers include `getRdmaInfo()`, `setUserdataForQuota()`, `getSupportedHeaderFeatureFlagsMask()`, `isMsgValid()`, `isValid()`. Declared payload/backing members include `RdmaInfo rdmaInfo`.

## Control Flow
Sender-side code builds `WriteLocalFileRDMAMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/PathInfo.h`, `common/storage/RdmaInfo.h`, `common/app/log/LogContext.h`, `common/net/message/session/rw/WriteLocalFileMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_WriteLocalFileRDMA`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
I/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_WriteLocalFileRDMA`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior. Validate control-message fields together with data-transfer or RDMA descriptor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRDMARespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRDMARespMsg.h

## Purpose
Defines `WriteLocalFileRDMARespMsg`, the response payload wrapper for BeeGFS storage I/O session RPCs using `NETMSGTYPE_WriteLocalFileRDMAResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`WriteLocalFileRDMARespMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_WriteLocalFileRDMAResp)` or an equivalent base constructor. Constructors include `WriteLocalFileRDMARespMsg(int64_t result) : SimpleInt64Msg(NETMSGTYPE_WriteLocalFileRDMAResp, result)`; `WriteLocalFileRDMARespMsg() : SimpleInt64Msg(NETMSGTYPE_WriteLocalFileRDMAResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `WriteLocalFileRDMARespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_WriteLocalFileRDMAResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
I/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_WriteLocalFileRDMAResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Validate control-message fields together with data-transfer or RDMA descriptor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRDMARespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRespMsg.h

## Purpose
Defines `WriteLocalFileRespMsg`, the response payload wrapper for BeeGFS storage I/O session RPCs using `NETMSGTYPE_WriteLocalFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`WriteLocalFileRespMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_WriteLocalFileResp)` or an equivalent base constructor. Constructors include `WriteLocalFileRespMsg(int64_t result) : SimpleInt64Msg(NETMSGTYPE_WriteLocalFileResp, result)`; `WriteLocalFileRespMsg() : SimpleInt64Msg(NETMSGTYPE_WriteLocalFileResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `WriteLocalFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage I/O session code path that handles `NETMSGTYPE_WriteLocalFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
I/o messages may pair serialized control data with socket payloads or rdma descriptors.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_WriteLocalFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Validate control-message fields together with data-transfer or RDMA descriptor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/session/rw/WriteLocalFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/GetHighResStatsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/GetHighResStatsMsg.h

## Purpose
Defines `GetHighResStatsMsg`, a BeeGFS storage target operation query/request message using `NETMSGTYPE_GetHighResStats`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetHighResStatsMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_GetHighResStats)` or an equivalent base constructor. Constructors include `GetHighResStatsMsg(int64_t lastStatsTimeMS) : SimpleInt64Msg(NETMSGTYPE_GetHighResStats, lastStatsTimeMS)`; `GetHighResStatsMsg() : SimpleInt64Msg(NETMSGTYPE_GetHighResStats)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetHighResStatsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_GetHighResStats`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetHighResStats`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/GetHighResStatsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/GetHighResStatsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/GetHighResStatsRespMsg.h

## Purpose
Defines `GetHighResStatsRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_GetHighResStatsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetHighResStatsRespMsg` derives from `public NetMessageSerdes<GetHighResStatsRespMsg>` and uses `BaseType(NETMSGTYPE_GetHighResStatsResp)` or an equivalent base constructor. Constructors include `GetHighResStatsRespMsg(HighResStatsList* statsList) : BaseType(NETMSGTYPE_GetHighResStatsResp)`; `GetHighResStatsRespMsg() : BaseType(NETMSGTYPE_GetHighResStatsResp)`. Serialization writes `backedPtr(obj->statsList, obj->parsed.statsList)`. Notable accessors/helpers include `getStatsList()`. Declared payload/backing members include `HighResStatsList* statsList`, `HighResStatsList statsList`.

## Control Flow
Sender-side code builds `GetHighResStatsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/HighResolutionStats.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_GetHighResStatsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetHighResStatsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/GetHighResStatsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/SetStorageTargetInfoMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/SetStorageTargetInfoMsg.h

## Purpose
Defines `SetStorageTargetInfoMsg`, a BeeGFS storage target operation command message using `NETMSGTYPE_SetStorageTargetInfo`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetStorageTargetInfoMsg` derives from `public NetMessageSerdes<SetStorageTargetInfoMsg>` and uses `BaseType(NETMSGTYPE_SetStorageTargetInfo)` or an equivalent base constructor. Constructors include `SetStorageTargetInfoMsg(NodeType nodeType, StorageTargetInfoList *targetInfoList) : BaseType(NETMSGTYPE_SetStorageTargetInfo)`; `SetStorageTargetInfoMsg() : BaseType(NETMSGTYPE_SetStorageTargetInfo)`. Serialization writes `nodeType`, `backedPtr(obj->targetInfoList, obj->parsed.targetInfoList)`. Notable accessors/helpers include `getNodeType()`, `getStorageTargetInfos()`. Declared payload/backing members include `StorageTargetInfoList* targetInfoList`, `int32_t nodeType`, `StorageTargetInfoList targetInfoList`.

## Control Flow
Sender-side code builds `SetStorageTargetInfoMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/storage/StorageTargetInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_SetStorageTargetInfo`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetStorageTargetInfo`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/SetStorageTargetInfoMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/SetStorageTargetInfoRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/SetStorageTargetInfoRespMsg.h

## Purpose
Defines `SetStorageTargetInfoRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_SetStorageTargetInfoResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetStorageTargetInfoRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_SetStorageTargetInfoResp)` or an equivalent base constructor. Constructors include `SetStorageTargetInfoRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_SetStorageTargetInfoResp, result)`; `SetStorageTargetInfoRespMsg() : SimpleIntMsg(NETMSGTYPE_SetStorageTargetInfoResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `SetStorageTargetInfoRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_SetStorageTargetInfoResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetStorageTargetInfoResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/SetStorageTargetInfoRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/StatStoragePathMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/StatStoragePathMsg.h

## Purpose
Defines `StatStoragePathMsg`, a BeeGFS storage target operation query/request message using `NETMSGTYPE_StatStoragePath`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`StatStoragePathMsg` derives from `public SimpleUInt16Msg` and uses `BaseType(NETMSGTYPE_StatStoragePath)` or an equivalent base constructor. Constructors include `StatStoragePathMsg(uint16_t targetID) : SimpleUInt16Msg(NETMSGTYPE_StatStoragePath, targetID)`; `StatStoragePathMsg() : SimpleUInt16Msg(NETMSGTYPE_StatStoragePath)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getTargetID()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `StatStoragePathMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleUInt16Msg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_StatStoragePath`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StatStoragePath`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/StatStoragePathMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/StatStoragePathRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/StatStoragePathRespMsg.h

## Purpose
Defines `StatStoragePathRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_StatStoragePathResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`StatStoragePathRespMsg` derives from `public NetMessageSerdes<StatStoragePathRespMsg>` and uses `BaseType(NETMSGTYPE_StatStoragePathResp)` or an equivalent base constructor. Constructors include `StatStoragePathRespMsg(int result, int64_t sizeTotal, int64_t sizeFree, int64_t inodesTotal, int64_t inodesFree) : BaseType(NETMSGTYPE_StatStoragePathResp)`; `StatStoragePathRespMsg() : BaseType(NETMSGTYPE_StatStoragePathResp)`. Serialization writes `result`, `sizeTotal`, `sizeFree`, `inodesTotal`, `inodesFree`. Notable accessors/helpers include `getResult()`, `getSizeTotal()`, `getSizeFree()`, `getInodesTotal()`, `getInodesFree()`. Declared payload/backing members include `int32_t result`, `int64_t sizeTotal`, `int64_t sizeFree`, `int64_t inodesTotal`, `int64_t inodesFree`.

## Control Flow
Sender-side code builds `StatStoragePathRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_StatStoragePathResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StatStoragePathResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/StatStoragePathRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncFileMsg.h

## Purpose
Defines `TruncFileMsg`, a BeeGFS storage target operation command message using `NETMSGTYPE_TruncFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`TruncFileMsg` derives from `public MirroredMessageBase<TruncFileMsg>` and uses `BaseType(NETMSGTYPE_TruncFile)` or an equivalent base constructor. Constructors include `TruncFileMsg(int64_t filesize, EntryInfo* entryInfo) : BaseType(NETMSGTYPE_TruncFile)`; `TruncFileMsg() : BaseType(NETMSGTYPE_TruncFile)`. Serialization writes `filesize`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `dynAttribs`, `mirroredTimestamps`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getFilesize()`, `getEntryInfo()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `int64_t filesize`, `FileEvent fileEvent`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `DynamicFileAttribsVec dynAttribs`, `MirroredTimestamps mirroredTimestamps`.

## Control Flow
Sender-side code builds `TruncFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_TruncFile`. Feature flags: `TRUNCFILEMSG_FLAG_USE_QUOTA`=1, `TRUNCFILEMSG_FLAG_HAS_EVENT`=2. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_TruncFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncFileRespMsg.h

## Purpose
Defines `TruncFileRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_TruncFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`TruncFileRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_TruncFileResp)` or an equivalent base constructor. Constructors include `TruncFileRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_TruncFileResp, result)`; `TruncFileRespMsg() : SimpleIntMsg(NETMSGTYPE_TruncFileResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `TruncFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_TruncFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_TruncFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileMsg.h

## Purpose
Defines `TruncLocalFileMsg`, a BeeGFS storage target operation command message using `NETMSGTYPE_TruncLocalFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`TruncLocalFileMsg` derives from `public NetMessageSerdes<TruncLocalFileMsg>` and uses `BaseType(NETMSGTYPE_TruncLocalFile)` or an equivalent base constructor. Constructors include `TruncLocalFileMsg(int64_t filesize, std::string& entryID, uint16_t targetID, PathInfo* pathInfo) : BaseType(NETMSGTYPE_TruncLocalFile)`; `TruncLocalFileMsg() : BaseType(NETMSGTYPE_TruncLocalFile)`. Serialization writes `filesize`, `userID`, `groupID`, `rawString(obj->entryID, obj->entryIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `getFilesize()`, `getEntryID()`, `getTargetID()`, `getPathInfo()`, `getUserID()`, `getGroupID()`, `setUserdataForQuota()`. Declared payload/backing members include `int64_t filesize`, `unsigned entryIDLen`, `const char* entryID`, `uint16_t targetID`, `uint32_t userID`, `uint32_t groupID`, `PathInfo* pathInfoPtr`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `TruncLocalFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/PathInfo.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_TruncLocalFile`. Feature flags: `TRUNCLOCALFILEMSG_FLAG_NODYNAMICATTRIBS`=1, `TRUNCLOCALFILEMSG_FLAG_USE_QUOTA`=2, `TRUNCLOCALFILEMSG_FLAG_BUDDYMIRROR`=4, `TRUNCLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_TruncLocalFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileRespMsg.h

## Purpose
Defines `TruncLocalFileRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_TruncLocalFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`TruncLocalFileRespMsg` derives from `public NetMessageSerdes<TruncLocalFileRespMsg>` and uses `BaseType(NETMSGTYPE_TruncLocalFileResp)` or an equivalent base constructor. Constructors include `TruncLocalFileRespMsg(FhgfsOpsErr result, int64_t filesize, int64_t allocedBlocks, int64_t modificationTimeSecs, int64_t lastAccessTimeSecs, uint64_t storageVersion) : BaseType(NETMSGTYPE_TruncLocalFileResp)`; `TruncLocalFileRespMsg() : BaseType(NETMSGTYPE_TruncLocalFileResp)`. Serialization writes `filesize`, `allocedBlocks`, `modificationTimeSecs`, `lastAccessTimeSecs`, `storageVersion`, `result`. Notable accessors/helpers include `getResult()`, `getFileSize()`, `getAllocedBlocks()`, `getModificationTimeSecs()`, `getLastAccessTimeSecs()`, `getStorageVersion()`. Declared payload/backing members include `int32_t result`, `int64_t filesize`, `int64_t modificationTimeSecs`, `int64_t lastAccessTimeSecs`, `uint64_t storageVersion`.

## Control Flow
Sender-side code builds `TruncLocalFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_TruncLocalFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_TruncLocalFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/TruncLocalFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetChunkFileAttribsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetChunkFileAttribsMsg.h

## Purpose
Defines `GetChunkFileAttribsMsg`, a BeeGFS metadata and storage attributes query/request message using `NETMSGTYPE_GetChunkFileAttribs`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetChunkFileAttribsMsg` derives from `public NetMessageSerdes<GetChunkFileAttribsMsg>` and uses `BaseType(NETMSGTYPE_GetChunkFileAttribs)` or an equivalent base constructor. Constructors include `GetChunkFileAttribsMsg(const std::string& entryID, uint16_t targetID, PathInfo* pathInfo) : BaseType(NETMSGTYPE_GetChunkFileAttribs)`; `GetChunkFileAttribsMsg() : BaseType(NETMSGTYPE_GetChunkFileAttribs)`. Serialization writes `rawString(obj->entryID, obj->entryIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getEntryID()`, `getTargetID()`, `getPathInfo()`. Declared payload/backing members include `unsigned entryIDLen`, `const char* entryID`, `uint16_t targetID`, `PathInfo* pathInfoPtr`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `GetChunkFileAttribsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetChunkFileAttribs`. Feature flags: `GETCHUNKFILEATTRSMSG_FLAG_BUDDYMIRROR`=1, `GETCHUNKFILEATTRSMSG_FLAG_BUDDYMIRROR_SECOND`=2.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetChunkFileAttribs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetChunkFileAttribsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetChunkFileAttribsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetChunkFileAttribsRespMsg.h

## Purpose
Defines `GetChunkFileAttribsRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_GetChunkFileAttribsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetChunkFileAttribsRespMsg` derives from `public NetMessageSerdes<GetChunkFileAttribsRespMsg>` and uses `BaseType(NETMSGTYPE_GetChunkFileAttribsResp)` or an equivalent base constructor. Constructors include `GetChunkFileAttribsRespMsg(FhgfsOpsErr result, int64_t size, int64_t allocedBlocks, int64_t modificationTimeSecs, int64_t lastAccessTimeSecs, uint64_t storageVersion) : BaseType(NETMSGTYPE_GetChunkFileAttribsResp)`; `GetChunkFileAttribsRespMsg() : BaseType(NETMSGTYPE_GetChunkFileAttribsResp)`. Serialization writes `size`, `allocedBlocks`, `modificationTimeSecs`, `lastAccessTimeSecs`, `storageVersion`, `result`. Notable accessors/helpers include `getResult()`, `getSize()`, `getAllocedBlocks()`, `getModificationTimeSecs()`, `getLastAccessTimeSecs()`, `getStorageVersion()`. Declared payload/backing members include `int32_t result`, `int64_t size`, `int64_t modificationTimeSecs`, `int64_t lastAccessTimeSecs`, `uint64_t storageVersion`.

## Control Flow
Sender-side code builds `GetChunkFileAttribsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetChunkFileAttribsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetChunkFileAttribsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetChunkFileAttribsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetEntryInfoMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetEntryInfoMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetEntryInfoRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetEntryInfoRespMsg.h

## Purpose
Defines `GetEntryInfoRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_GetEntryInfoResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetEntryInfoRespMsg` derives from `public NetMessageSerdes<GetEntryInfoRespMsg>` and uses `BaseType(NETMSGTYPE_GetEntryInfoResp)` or an equivalent base constructor. Constructors include `GetEntryInfoRespMsg(FhgfsOpsErr result, StripePattern* pattern, uint16_t mirrorNodeID, PathInfo* pathInfoPtr, RemoteStorageTarget* rst, uint32_t numSessionsRead = 0, uint32_t numSessionsWrite = 0, uint8_t dataState = 0) : BaseType(NETMSGTYPE_GetEntryInfoResp)`; `GetEntryInfoRespMsg() : BaseType(NETMSGTYPE_GetEntryInfoResp)`. Serialization writes `result`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `backedPtr(obj->rstPtr, obj->rst)`, `mirrorNodeID`, `numSessionsRead`, `numSessionsWrite`, `fileDataState`. Notable accessors/helpers include `getPattern()`, `getResult()`, `getMirrorNodeID()`, `getPathInfo()`, `getRemoteStorageTarget()`, `getNumSessionsRead()`, `getNumSessionsWrite()`, `getFileDataState()`. Declared payload/backing members include `int32_t result`, `uint32_t numSessionsRead`, `uint32_t numSessionsWrite`, `uint8_t  fileDataState`, `StripePattern* pattern`, `PathInfo* pathInfoPtr`, `RemoteStorageTarget* rstPtr`, `RemoteStorageTarget rst`, `std::unique_ptr<StripePattern> pattern`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `GetEntryInfoRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/StripePattern.h`, `common/storage/RemoteStorageTarget.h`, `common/storage/StorageErrors.h`, `common/storage/PathInfo.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetEntryInfoResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetEntryInfoResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetEntryInfoRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetXAttrMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetXAttrMsg.h

## Purpose
Defines `GetXAttrMsg`, a BeeGFS metadata and storage attributes query/request message using `NETMSGTYPE_GetXAttr`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetXAttrMsg` derives from `public MirroredMessageBase<GetXAttrMsg>` and uses `BaseType(NETMSGTYPE_GetXAttr)` or an equivalent base constructor. Constructors include `GetXAttrMsg(EntryInfo* entryInfo, const std::string& name, int size) : BaseType(NETMSGTYPE_GetXAttr), entryInfoPtr(entryInfo), size(size), name(name)`; `GetXAttrMsg() : BaseType(NETMSGTYPE_GetXAttr)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `name`, `size`. Notable accessors/helpers include `supportsMirroring()`, `getEntryInfo()`, `getName()`, `getSize()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `int32_t size`, `std::string name`.

## Control Flow
Sender-side code builds `GetXAttrMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetXAttr`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetXAttr`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetXAttrRespMsg.h

## Purpose
Defines `GetXAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_GetXAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetXAttrRespMsg` derives from `public NetMessageSerdes<GetXAttrRespMsg>` and uses `BaseType(NETMSGTYPE_GetXAttrResp)` or an equivalent base constructor. Constructors include `GetXAttrRespMsg(const CharVector& value, int size, int returnCode) : BaseType(NETMSGTYPE_GetXAttrResp), value(value), size(size), returnCode(returnCode)`; `GetXAttrRespMsg() : BaseType(NETMSGTYPE_GetXAttrResp)`. Serialization writes `value`, `size`, `returnCode`. Notable accessors/helpers include `getValue()`, `getReturnCode()`, `getSize()`. Declared payload/backing members include `CharVector value`, `int32_t size`, `int32_t returnCode`.

## Control Flow
Sender-side code builds `GetXAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/app/log/LogContext.h`, `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetXAttrResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetXAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/ListXAttrMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/ListXAttrMsg.h

## Purpose
Defines `ListXAttrMsg`, a BeeGFS metadata and storage attributes query/request message using `NETMSGTYPE_ListXAttr`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`ListXAttrMsg` derives from `public MirroredMessageBase<ListXAttrMsg>` and uses `BaseType(NETMSGTYPE_ListXAttr)` or an equivalent base constructor. Constructors include `ListXAttrMsg(EntryInfo* entryInfo, int size) : BaseType(NETMSGTYPE_ListXAttr), entryInfoPtr(entryInfo), size(size)`; `ListXAttrMsg() : BaseType(NETMSGTYPE_ListXAttr)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `size`. Notable accessors/helpers include `supportsMirroring()`, `getEntryInfo()`, `getSize()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `int32_t size`.

## Control Flow
Sender-side code builds `ListXAttrMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_ListXAttr`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListXAttr`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/ListXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/ListXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/ListXAttrRespMsg.h

## Purpose
Defines `ListXAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_ListXAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`ListXAttrRespMsg` derives from `public NetMessageSerdes<ListXAttrRespMsg>` and uses `BaseType(NETMSGTYPE_ListXAttrResp)` or an equivalent base constructor. Constructors include `ListXAttrRespMsg(const StringVector& value, int size, int returnCode) : BaseType(NETMSGTYPE_ListXAttrResp), value(value), size(size), returnCode(returnCode)`; `ListXAttrRespMsg() : BaseType(NETMSGTYPE_ListXAttrResp)`. Serialization writes `value`, `size`, `returnCode`. Notable accessors/helpers include `getValue()`, `getReturnCode()`, `getSize()`. Declared payload/backing members include `StringVector value`, `int32_t size`, `int32_t returnCode`.

## Control Flow
Sender-side code builds `ListXAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/app/log/LogContext.h`, `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_ListXAttrResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListXAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/ListXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.h

## Purpose
Defines `RefreshEntryInfoMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_RefreshEntryInfo`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RefreshEntryInfoMsg` derives from `public MirroredMessageBase<RefreshEntryInfoMsg>` and uses `BaseType(NETMSGTYPE_RefreshEntryInfo)` or an equivalent base constructor. Constructors include `RefreshEntryInfoMsg(EntryInfo* entryInfo) : BaseType(NETMSGTYPE_RefreshEntryInfo)`; `RefreshEntryInfoMsg() : BaseType(NETMSGTYPE_RefreshEntryInfo)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `fileTimestamps`. Notable accessors/helpers include `getEntryInfo()`, `supportsMirroring()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `MirroredTimestamps fileTimestamps`.

## Control Flow
Sender-side code builds `RefreshEntryInfoMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_RefreshEntryInfo`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshEntryInfo`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h

## Purpose
Defines `RefreshEntryInfoRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_RefreshEntryInfoResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RefreshEntryInfoRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RefreshEntryInfoResp)` or an equivalent base constructor. Constructors include `RefreshEntryInfoRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_RefreshEntryInfoResp, result)`; `RefreshEntryInfoRespMsg() : SimpleIntMsg(NETMSGTYPE_RefreshEntryInfoResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RefreshEntryInfoRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_RefreshEntryInfoResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshEntryInfoResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RemoveXAttrMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RemoveXAttrMsg.h

## Purpose
Defines `RemoveXAttrMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_RemoveXAttr`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RemoveXAttrMsg` derives from `public MirroredMessageBase<RemoveXAttrMsg>` and uses `BaseType(NETMSGTYPE_RemoveXAttr)` or an equivalent base constructor. Constructors include `RemoveXAttrMsg(EntryInfo* entryInfo, const std::string& name) : BaseType(NETMSGTYPE_RemoveXAttr)`; `RemoveXAttrMsg() : BaseType(NETMSGTYPE_RemoveXAttr)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `name`, `inodeTimestamps`. Notable accessors/helpers include `getEntryInfo()`, `getName()`, `supportsMirroring()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `std::string name`, `MirroredTimestamps inodeTimestamps`.

## Control Flow
Sender-side code builds `RemoveXAttrMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_RemoveXAttr`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveXAttr`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RemoveXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RemoveXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RemoveXAttrRespMsg.h

## Purpose
Defines `RemoveXAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_RemoveXAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RemoveXAttrRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RemoveXAttrResp)` or an equivalent base constructor. Constructors include `RemoveXAttrRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_RemoveXAttrResp, result)`; `RemoveXAttrRespMsg() : SimpleIntMsg(NETMSGTYPE_RemoveXAttrResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RemoveXAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_RemoveXAttrResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RemoveXAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/RemoveXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetAttrMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetAttrMsg.h

## Purpose
Defines `SetAttrMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetAttr`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetAttrMsg` derives from `public MirroredMessageBase<SetAttrMsg>` and uses `BaseType(NETMSGTYPE_SetAttr)` or an equivalent base constructor. Constructors include `SetAttrMsg(EntryInfo *entryInfo, int validAttribs, SettableFileAttribs* attribs) : BaseType(NETMSGTYPE_SetAttr), validAttribs(validAttribs), attribs(*attribs), entryInfoPtr(entryInfo)`; `SetAttrMsg() : BaseType(NETMSGTYPE_SetAttr)`. Serialization writes `validAttribs`, `attribs`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `inodeTimestamps`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getValidAttribs()`, `getAttribs()`, `getEntryInfo()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`, `supportsMirroring()`. Declared payload/backing members include `int32_t validAttribs`, `SettableFileAttribs attribs`, `FileEvent fileEvent`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `MirroredTimestamps inodeTimestamps`.

## Control Flow
Sender-side code builds `SetAttrMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`, `common/storage/StorageDefinitions.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetAttr`. Feature flags: `SETATTRMSG_FLAG_USE_QUOTA`=1, `SETATTRMSG_FLAG_HAS_EVENT`=4, `SETATTRMSG_FLAG_INCR_NLINKCNT`=8, `SETATTRMSG_FLAG_DECR_NLINKCNT`=16. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetAttr`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetAttrRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetAttrRespMsg.h

## Purpose
Defines `SetAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_SetAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetAttrRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_SetAttrResp)` or an equivalent base constructor. Constructors include `SetAttrRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_SetAttrResp, result)`; `SetAttrRespMsg() : SimpleIntMsg(NETMSGTYPE_SetAttrResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `SetAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetAttrResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetDirPatternMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetDirPatternMsg.h

## Purpose
Defines `SetDirPatternMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetDirPattern`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetDirPatternMsg` derives from `public MirroredMessageBase<SetDirPatternMsg>` and uses `BaseType(NETMSGTYPE_SetDirPattern)` or an equivalent base constructor. Constructors include `SetDirPatternMsg(EntryInfo* entryInfo, StripePattern* pattern, RemoteStorageTarget* rst) : BaseType(NETMSGTYPE_SetDirPattern)`; `SetDirPatternMsg() : BaseType(NETMSGTYPE_SetDirPattern)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `backedPtr(obj->rstPtr, obj->rst)`, `uid`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `getPattern()`, `getEntryInfo()`, `getRemoteStorageTarget()`, `getUID()`, `setUID()`, `setMsgHeaderFeatureFlags()`, `supportsMirroring()`. Declared payload/backing members include `static const uint32_t HAS_UID`, `uint32_t uid`, `EntryInfo* entryInfoPtr`, `StripePattern* pattern`, `RemoteStorageTarget* rstPtr`, `EntryInfo entryInfo`, `RemoteStorageTarget rst`, `std::unique_ptr<StripePattern> pattern`.

## Control Flow
Sender-side code builds `SetDirPatternMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/StripePattern.h`, `common/storage/EntryInfo.h`, `common/storage/RemoteStorageTarget.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetDirPattern`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetDirPattern`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetDirPatternMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetDirPatternRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetDirPatternRespMsg.h

## Purpose
Defines `SetDirPatternRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_SetDirPatternResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetDirPatternRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_SetDirPatternResp)` or an equivalent base constructor. Constructors include `SetDirPatternRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_SetDirPatternResp, result)`; `SetDirPatternRespMsg() : SimpleIntMsg(NETMSGTYPE_SetDirPatternResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `SetDirPatternRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetDirPatternResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetDirPatternResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetDirPatternRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFilePatternMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFilePatternMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFilePatternRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFilePatternRespMsg.h

## Purpose
Defines `SetFilePatternRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_SetFilePatternResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetFilePatternRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_SetFilePatternResp)` or an equivalent base constructor. Constructors include `SetFilePatternRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_SetFilePatternResp, result)`; `SetFilePatternRespMsg() : SimpleIntMsg(NETMSGTYPE_SetFilePatternResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `SetFilePatternRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetFilePatternResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetFilePatternResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFilePatternRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFileStateMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFileStateMsg.h

## Purpose
Defines `SetFileStateMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetFileState`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetFileStateMsg` derives from `public MirroredMessageBase<SetFileStateMsg>` and uses `BaseType(NETMSGTYPE_SetFileState)` or an equivalent base constructor. Constructors include `SetFileStateMsg(EntryInfo* entryInfo, uint8_t state) : BaseType(NETMSGTYPE_SetFileState)`; `SetFileStateMsg() : BaseType(NETMSGTYPE_SetFileState)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `state`. Notable accessors/helpers include `getEntryInfo()`, `getFileState()`, `supportsMirroring()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `uint8_t state`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `SetFileStateMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetFileState`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetFileState`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFileStateMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFileStateRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFileStateRespMsg.h

## Purpose
Defines `SetFileStateRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_SetFileStateResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetFileStateRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_SetFileStateResp)` or an equivalent base constructor. Constructors include `SetFileStateRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_SetFileStateResp, result)`; `SetFileStateRespMsg() : SimpleIntMsg(NETMSGTYPE_SetFileStateResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `SetFileStateRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`, `common/storage/StorageErrors.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetFileStateResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetFileStateResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetFileStateRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetLocalAttrMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetLocalAttrMsg.h

## Purpose
Defines `SetLocalAttrMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetLocalAttr`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetLocalAttrMsg` derives from `public NetMessageSerdes<SetLocalAttrMsg>` and uses `BaseType(NETMSGTYPE_SetLocalAttr)` or an equivalent base constructor. Constructors include `SetLocalAttrMsg(std::string& entryID, uint16_t targetID, PathInfo* pathInfo, int validAttribs, SettableFileAttribs* attribs, bool enableCreation) : BaseType(NETMSGTYPE_SetLocalAttr)`; `SetLocalAttrMsg() : BaseType(NETMSGTYPE_SetLocalAttr)`. Serialization writes `attribs`, `validAttribs`, `rawString(obj->entryID, obj->entryIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`, `enableCreation`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getEntryID()`, `getTargetID()`, `getValidAttribs()`, `getAttribs()`, `getEnableCreation()`, `getPathInfo()`. Declared payload/backing members include `unsigned entryIDLen`, `const char* entryID`, `uint16_t targetID`, `int32_t validAttribs`, `SettableFileAttribs attribs`, `bool enableCreation`, `PathInfo* pathInfoPtr`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `SetLocalAttrMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/PathInfo.h`, `common/storage/StorageDefinitions.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetLocalAttr`. Feature flags: `SETLOCALATTRMSG_FLAG_USE_QUOTA`=1, `SETLOCALATTRMSG_FLAG_BUDDYMIRROR`=2, `SETLOCALATTRMSG_FLAG_BUDDYMIRROR_SECOND`=4.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetLocalAttr`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetLocalAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetLocalAttrRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetLocalAttrRespMsg.h

## Purpose
Defines `SetLocalAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_SetLocalAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetLocalAttrRespMsg` derives from `public NetMessageSerdes<SetLocalAttrRespMsg>` and uses `BaseType(NETMSGTYPE_SetLocalAttrResp)` or an equivalent base constructor. Constructors include `SetLocalAttrRespMsg(FhgfsOpsErr result, DynamicFileAttribs& dynamicAttribs) : BaseType(NETMSGTYPE_SetLocalAttrResp), result(result), filesize(dynamicAttribs.fileSize), numBlocks(dynamicAttribs.numBlocks), modificationTimeSecs(dynamicAttribs.modificationTimeSecs), lastAccessTimeSecs(dynamicAttribs.lastAccessTimeSecs), storageVersion(dynamicAttribs.storageVersion)`; `SetLocalAttrRespMsg(FhgfsOpsErr result) : BaseType(NETMSGTYPE_SetLocalAttrResp), result(result), filesize(0), numBlocks(0), modificationTimeSecs(0), lastAccessTimeSecs(0), storageVersion(0)`; `SetLocalAttrRespMsg() : BaseType(NETMSGTYPE_SetLocalAttrResp)`. Serialization writes `filesize`, `numBlocks`, `modificationTimeSecs`, `lastAccessTimeSecs`, `storageVersion`, `result`. Notable accessors/helpers include `getResult()`, `getDynamicAttribs()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `FhgfsOpsErr result`, `int64_t filesize`, `int64_t numBlocks`, `int64_t modificationTimeSecs`, `int64_t lastAccessTimeSecs`, `uint64_t storageVersion`.

## Control Flow
Sender-side code builds `SetLocalAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/striping/DynamicFileAttribs.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetLocalAttrResp`. Feature flags: `SETLOCALATTRRESPMSG_FLAG_HAS_ATTRS`=1.

## Risks And Edge Cases
Feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetLocalAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetLocalAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetXAttrMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetXAttrMsg.h

## Purpose
Defines `SetXAttrMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_SetXAttr`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`SetXAttrMsg` derives from `public MirroredMessageBase<SetXAttrMsg>` and uses `BaseType(NETMSGTYPE_SetXAttr)` or an equivalent base constructor. Constructors include `SetXAttrMsg(EntryInfo* entryInfo, const std::string& name, const CharVector& value, int flags) : BaseType(NETMSGTYPE_SetXAttr)`; `SetXAttrMsg() : BaseType(NETMSGTYPE_SetXAttr)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `name`, `value`, `flags`, `inodeTimestamps`. Notable accessors/helpers include `getEntryInfo()`, `getName()`, `getValue()`, `getFlags()`, `supportsMirroring()`. Declared payload/backing members include `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`, `std::string name`, `CharVector value`, `int32_t flags`, `MirroredTimestamps inodeTimestamps`.

## Control Flow
Sender-side code builds `SetXAttrMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetXAttr`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetXAttr`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetXAttrRespMsg.h

## Purpose
Defines `SetXAttrRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_SetXAttrResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`SetXAttrRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_SetXAttrResp)` or an equivalent base constructor. Constructors include `SetXAttrRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_SetXAttrResp, result)`; `SetXAttrRespMsg() : SimpleIntMsg(NETMSGTYPE_SetXAttrResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `SetXAttrRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_SetXAttrResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_SetXAttrResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/SetXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/StatMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/StatMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/StatRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/StatRespMsg.h

## Purpose
Defines `StatRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_StatResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`StatRespMsg` derives from `public NetMessageSerdes<StatRespMsg>` and uses `BaseType(NETMSGTYPE_StatResp)` or an equivalent base constructor. Constructors include `StatRespMsg(int result, StatData statData) : BaseType(NETMSGTYPE_StatResp)`; `StatRespMsg() : BaseType(NETMSGTYPE_StatResp)`. Serialization writes `result`, `statData`, `stringAlign4(obj->parentEntryID)`, `parentNodeID`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `getResult()`, `getStatData()`, `getParentNodeID()`. Declared payload/backing members include `int32_t result`, `StatData statData`, `NumNodeID parentNodeID`, `std::string parentEntryID`.

## Control Flow
Sender-side code builds `StatRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/Metadata.h`, `common/storage/StatData.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_StatResp`. Feature flags: `STATRESPMSG_FLAG_HAS_PARENTINFO`=1.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StatResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/StatRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/UpdateDirParentMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/UpdateDirParentMsg.h

## Purpose
Defines `UpdateDirParentMsg`, a BeeGFS metadata and storage attributes command message using `NETMSGTYPE_UpdateDirParent`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UpdateDirParentMsg` derives from `public MirroredMessageBase<UpdateDirParentMsg>` and uses `BaseType(NETMSGTYPE_UpdateDirParent)` or an equivalent base constructor. Constructors include `UpdateDirParentMsg(EntryInfo* entryInfoPtr, NumNodeID parentOwnerNodeID) : BaseType(NETMSGTYPE_UpdateDirParent)`; `UpdateDirParentMsg() : BaseType(NETMSGTYPE_UpdateDirParent)`. Serialization writes `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `parentOwnerNodeID`, `dirTimestamps`. Notable accessors/helpers include `getEntryInfo()`, `getParentNodeID()`, `supportsMirroring()`. Declared payload/backing members include `NumNodeID parentOwnerNodeID`, `EntryInfo entryInfo`, `MirroredTimestamps dirTimestamps`.

## Control Flow
Sender-side code builds `UpdateDirParentMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/EntryInfo.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_UpdateDirParent`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateDirParent`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/UpdateDirParentMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/UpdateDirParentRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/UpdateDirParentRespMsg.h

## Purpose
Defines `UpdateDirParentRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_UpdateDirParentResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UpdateDirParentRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_UpdateDirParentResp)` or an equivalent base constructor. Constructors include `UpdateDirParentRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_UpdateDirParentResp, result)`; `UpdateDirParentRespMsg() : SimpleIntMsg(NETMSGTYPE_UpdateDirParentResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `UpdateDirParentRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_UpdateDirParentResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateDirParentResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/UpdateDirParentRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/CpChunkPathsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/CpChunkPathsMsg.h

## Purpose
Defines `CpChunkPathsMsg`, a BeeGFS chunk balancing command message using `NETMSGTYPE_CpChunkPaths`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`CpChunkPathsMsg` derives from `public NetMessageSerdes<CpChunkPathsMsg>` and uses `BaseType(NETMSGTYPE_CpChunkPaths)` or an equivalent base constructor. Constructors include `CpChunkPathsMsg(uint16_t targetID, uint16_t destinationID, EntryInfo* entryInfo, std::string* relativePath, FileEvent* fileEvent) : BaseType(NETMSGTYPE_CpChunkPaths)`; `CpChunkPathsMsg() : BaseType(NETMSGTYPE_CpChunkPaths)`. Serialization writes `targetID`, `destinationID`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `backedPtr(obj->relativePath, obj->parsed.relativePath)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `getTargetID()`, `getDestinationID()`, `getRelativePath()`, `getEntryInfo()`, `getFileEvent()`. Declared payload/backing members include `uint16_t targetID`, `uint16_t destinationID`, `FileEvent fileEvent`, `std::string* relativePath`, `EntryInfo* entryInfoPtr`, `std::string relativePath`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `CpChunkPathsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/toolkit/serialization/Serialization.h`, `common/storage/FileEvent.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_CpChunkPaths`. Feature flags: `CPCHUNKPATHSMSG_FLAG_BUDDYMIRROR`=1, `CPCHUNKPATHSMSG_FLAG_HAS_EVENT`=2.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CpChunkPaths`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/CpChunkPathsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/CpChunkPathsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/CpChunkPathsRespMsg.h

## Purpose
Defines `CpChunkPathsRespMsg`, the response payload wrapper for BeeGFS chunk balancing RPCs using `NETMSGTYPE_CpChunkPathsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`CpChunkPathsRespMsg` derives from `public NetMessageSerdes<CpChunkPathsRespMsg>` and uses `BaseType(NETMSGTYPE_CpChunkPathsResp)` or an equivalent base constructor. Constructors include `CpChunkPathsRespMsg(FhgfsOpsErr result ) : BaseType(NETMSGTYPE_CpChunkPathsResp)`; `CpChunkPathsRespMsg() : BaseType(NETMSGTYPE_CpChunkPathsResp)`. Serialization writes `result`. Notable accessors/helpers include `getResult()`. Declared payload/backing members include `int32_t result`.

## Control Flow
Sender-side code builds `CpChunkPathsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_CpChunkPathsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_CpChunkPathsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/CpChunkPathsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsg.h

## Purpose
Defines `GetChunkBalanceJobStatsMsg`, a BeeGFS chunk balancing query/request message using `NETMSGTYPE_GetChunkBalanceJobStats`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetChunkBalanceJobStatsMsg` derives from `public SimpleMsg` and uses `BaseType(NETMSGTYPE_GetChunkBalanceJobStats)` or an equivalent base constructor. Constructors include `GetChunkBalanceJobStatsMsg() : SimpleMsg(NETMSGTYPE_GetChunkBalanceJobStats)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetChunkBalanceJobStatsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_GetChunkBalanceJobStats`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetChunkBalanceJobStats`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsRespMsg.h

## Purpose
Defines `GetChunkBalanceJobStatsRespMsg`, the response payload wrapper for BeeGFS chunk balancing RPCs using `NETMSGTYPE_GetChunkBalanceJobStatsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetChunkBalanceJobStatsRespMsg` derives from `public NetMessageSerdes<GetChunkBalanceJobStatsRespMsg>` and uses `BaseType(NETMSGTYPE_GetChunkBalanceJobStatsResp)` or an equivalent base constructor. Constructors include `GetChunkBalanceJobStatsRespMsg(ChunkBalancerJobStatistics* jobStats) : BaseType(NETMSGTYPE_GetChunkBalanceJobStatsResp), jobStatsPtr(jobStats)`; `GetChunkBalanceJobStatsRespMsg() : BaseType(NETMSGTYPE_GetChunkBalanceJobStatsResp)`. Serialization writes `backedPtr(obj->jobStatsPtr, obj->jobStats)`. Notable accessors/helpers include `getJobStats()`. Declared payload/backing members include `ChunkBalancerJobStatistics* jobStatsPtr`, `ChunkBalancerJobStatistics jobStats`.

## Control Flow
Sender-side code builds `GetChunkBalanceJobStatsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/chunkbalancer/ChunkBalancerJobStatistics.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_GetChunkBalanceJobStatsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetChunkBalanceJobStatsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/StartChunkBalanceMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/StartChunkBalanceMsg.h

## Purpose
Defines `StartChunkBalanceMsg`, a BeeGFS chunk balancing command message using `NETMSGTYPE_StartChunkBalance`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`StartChunkBalanceMsg` derives from `public MirroredMessageBase<StartChunkBalanceMsg>` and uses `BaseType(NETMSGTYPE_StartChunkBalance)` or an equivalent base constructor. Constructors include `StartChunkBalanceMsg(uint8_t idType, std::string relativePath, const UInt16Vector* targetIDs, const UInt16Vector* destinationIDs, EntryInfo* entryInfo) : BaseType(NETMSGTYPE_StartChunkBalance)`; `StartChunkBalanceMsg() : BaseType(NETMSGTYPE_StartChunkBalance)`. Serialization writes `idType`, `relativePath`, `backedPtr(obj->targetIDsPtr, obj->targetIDs)`, `backedPtr(obj->destinationIDsPtr, obj->destinationIDs)`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getIdType()`, `getTargetIDs()`, `getDestinationIDs()`, `getRelativePath()`, `getEntryInfo()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `uint8_t idType`, `std::string relativePath`, `FileEvent fileEvent`, `EntryInfo* entryInfoPtr`, `const UInt16Vector* targetIDsPtr`, `const UInt16Vector* destinationIDsPtr`, `UInt16Vector targetIDs`, `UInt16Vector destinationIDs`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `StartChunkBalanceMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`, `common/storage/EntryInfo.h`, `components/chunkbalancer/SyncCandidate.h`, `common/storage/FileEvent.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_StartChunkBalance`. Feature flags: `STARTCHUNKBALANCEMSG_FLAG_HAS_EVENT`=1. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StartChunkBalance`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/StartChunkBalanceMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/StartChunkBalanceRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/StartChunkBalanceRespMsg.h

## Purpose
Defines `StartChunkBalanceRespMsg`, the response payload wrapper for BeeGFS chunk balancing RPCs using `NETMSGTYPE_StartChunkBalanceResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`StartChunkBalanceRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_StartChunkBalanceResp)` or an equivalent base constructor. Constructors include `StartChunkBalanceRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_StartChunkBalanceResp, result)`; `StartChunkBalanceRespMsg() : SimpleIntMsg(NETMSGTYPE_StartChunkBalanceResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `StartChunkBalanceRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_StartChunkBalanceResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StartChunkBalanceResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/StartChunkBalanceRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/UpdateStripePatternMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/UpdateStripePatternMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/UpdateStripePatternRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/UpdateStripePatternRespMsg.h

## Purpose
Defines `UpdateStripePatternRespMsg`, the response payload wrapper for BeeGFS chunk balancing RPCs using `NETMSGTYPE_UpdateStripePatternResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UpdateStripePatternRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_UpdateStripePatternResp)` or an equivalent base constructor. Constructors include `UpdateStripePatternRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_UpdateStripePatternResp, result)`; `UpdateStripePatternRespMsg() : SimpleIntMsg(NETMSGTYPE_UpdateStripePatternResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `UpdateStripePatternRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_UpdateStripePatternResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateStripePatternResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/UpdateStripePatternRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/HardlinkMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/HardlinkMsg.h

## Purpose
Defines `HardlinkMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_Hardlink`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`HardlinkMsg` derives from `public MirroredMessageBase<HardlinkMsg>` and uses `BaseType(NETMSGTYPE_Hardlink)` or an equivalent base constructor. Constructors include `HardlinkMsg(EntryInfo* fromDirInfo, std::string& fromName, EntryInfo* fromInfo, EntryInfo* toDirInfo, std::string& toName) : BaseType(NETMSGTYPE_Hardlink)`; `HardlinkMsg() : BaseType(NETMSGTYPE_Hardlink)`. Serialization writes `backedPtr(obj->fromInfoPtr, obj->fromInfo)`, `backedPtr(obj->toDirInfoPtr, obj->toDirInfo)`, `stringAlign4(obj->toName)`, `fromDirInfoPtr`, `backedPtr(obj->fromDirInfoPtr, obj->fromDirInfo)`, `stringAlign4(obj->fromName)`, `fileEvent`, `dirTimestamps`, `fileTimestamps`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getFromInfo()`, `getFromDirInfo()`, `getToDirInfo()`, `getFromName()`, `getToName()`, `supportsMirroring()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `std::string fromName`, `std::string toName`, `FileEvent fileEvent`, `EntryInfo* fromInfoPtr`, `EntryInfo* fromDirInfoPtr`, `EntryInfo* toDirInfoPtr`, `EntryInfo fromInfo`, `EntryInfo fromDirInfo`, `EntryInfo toDirInfo`, `MirroredTimestamps dirTimestamps`, `MirroredTimestamps fileTimestamps`.

## Control Flow
Sender-side code builds `HardlinkMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_Hardlink`. Feature flags: `HARDLINKMSG_FLAG_IS_TO_DENTRY_CREATE`=1, `HARDLINKMSG_FLAG_HAS_EVENT`=2. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_Hardlink`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/HardlinkMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/HardlinkRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/HardlinkRespMsg.h

## Purpose
Defines `HardlinkRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_HardlinkResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`HardlinkRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_HardlinkResp)` or an equivalent base constructor. Constructors include `HardlinkRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_HardlinkResp, result)`; `HardlinkRespMsg() : SimpleIntMsg(NETMSGTYPE_HardlinkResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `HardlinkRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_HardlinkResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_HardlinkResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/HardlinkRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkDirMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkDirMsg.h

## Purpose
Defines `MkDirMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_MkDir`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`MkDirMsg` derives from `public MirroredMessageBase<MkDirMsg>` and uses `BaseType(NETMSGTYPE_MkDir)` or an equivalent base constructor. Constructors include `MkDirMsg(const EntryInfo* parentEntryInfo, const std::string& newDirName, const unsigned userID, const unsigned groupID, const int mode, const int umask, const UInt16List* preferredNodes) : BaseType(NETMSGTYPE_MkDir), userID(userID), groupID(groupID), mode(mode), umask(umask), newDirName(newDirName.c_str() ), newDirNameLen(newDirName.length() ), parentEntryInfoPtr(parentEntryInfo), preferredNodes(preferredNodes)`; `MkDirMsg() : BaseType(NETMSGTYPE_MkDir)`. Serialization writes `userID`, `groupID`, `mode`, `umask`, `backedPtr(obj->parentEntryInfoPtr, obj->parentEntryInfo)`, `backedPtr(obj->createdEntryInfoPtr, obj->createdEntryInfo)`, `parentTimestamps`, `rawString(obj->newDirName, obj->newDirNameLen, 4)`, `backedPtr(obj->preferredNodes, obj->parsed.preferredNodes)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getSupportedHeaderFeatureFlagsMask()`, `setMode()`, `getPreferredNodes()`, `getUserID()`, `getGroupID()`, `getMode()`, `getUmask()`, `getParentInfo()`, `getNewDirName()`, `getCreatedEntryInfo()`, and additional getters/setters. Declared payload/backing members include `uint32_t userID`, `uint32_t groupID`, `int32_t mode`, `int32_t umask`, `FileEvent fileEvent`, `const char* newDirName`, `unsigned newDirNameLen`, `const EntryInfo* parentEntryInfoPtr`, `const UInt16List* preferredNodes`, `EntryInfo* createdEntryInfoPtr`, `EntryInfo parentEntryInfo`, `UInt16List preferredNodes`, `EntryInfo createdEntryInfo`, `MirroredTimestamps parentTimestamps`.

## Control Flow
Sender-side code builds `MkDirMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkDir`. Feature flags: `MKDIRMSG_FLAG_NOMIRROR`=1, `MKDIRMSG_FLAG_HAS_EVENT`=4. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkDir`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkDirMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkDirRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkDirRespMsg.h

## Purpose
Defines `MkDirRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MkDirResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MkDirRespMsg` derives from `public NetMessageSerdes<MkDirRespMsg>` and uses `BaseType(NETMSGTYPE_MkDirResp)` or an equivalent base constructor. Constructors include `MkDirRespMsg(int result, EntryInfo* entryInfo) : BaseType(NETMSGTYPE_MkDirResp)`; `MkDirRespMsg() : BaseType(NETMSGTYPE_MkDirResp)`. Serialization writes `result`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`. Notable accessors/helpers include `getResult()`, `getEntryInfo()`. Declared payload/backing members include `int32_t result`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `MkDirRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkDirResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkDirResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkDirRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileMsg.h

## Purpose
Defines `MkFileMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_MkFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`MkFileMsg` derives from `public MirroredMessageBase<MkFileMsg>` and uses `BaseType(NETMSGTYPE_MkFile)` or an equivalent base constructor. Constructors include `MkFileMsg(const EntryInfo* parentInfo, const std::string& newName, const unsigned userID, const unsigned groupID, const int mode, const int umask, const UInt16List* preferredTargets) : BaseType(NETMSGTYPE_MkFile), newName(newName.c_str() ), newNameLen(newName.length() ), userID(userID), groupID(groupID), mode(mode), umask(umask), parentInfoPtr(parentInfo), preferredTargets(preferredTargets)`; `MkFileMsg() : BaseType(NETMSGTYPE_MkFile)`. Serialization writes `userID`, `groupID`, `mode`, `umask`, `numtargets`, `chunksize`, `storagePoolId`, `backedPtr(obj->parentInfoPtr, obj->parentInfo)`, `rawString(obj->newName, obj->newNameLen, 4)`, `rawString(obj->newEntryID, obj->newEntryIDLen, 4)`, `backedPtr(obj->pattern, obj->parsed.pattern)`, `backedPtr(obj->rstPtr, obj->rstInfo)`, `dirTimestamps`, `createTime`, `backedPtr(obj->preferredTargets, obj->parsed.preferredTargets)`, `fileEvent`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getSupportedHeaderFeatureFlagsMask()`, `getPreferredNodes()`, `getUserID()`, `getGroupID()`, `getMode()`, `getUmask()`, `getNewName()`, `getParentInfo()`, `setStripeHints()`, `getNumTargets()`, and additional getters/setters. Declared payload/backing members include `MirroredTimestamps dirTimestamps`, `int64_t createTime`, `const char* newName`, `unsigned newNameLen`, `uint32_t userID`, `uint32_t groupID`, `int32_t mode`, `int32_t umask`, `uint32_t numtargets`, `uint32_t chunksize`, `FileEvent fileEvent`, `StoragePoolId storagePoolId`, `const char* newEntryID`, `unsigned newEntryIDLen`, plus additional backing fields.

## Control Flow
Sender-side code builds `MkFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/StatData.h`, `common/storage/striping/StripePattern.h`, `common/storage/RemoteStorageTarget.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkFile`. Feature flags: `MKFILEMSG_FLAG_STRIPEHINTS`=1, `MKFILEMSG_FLAG_STORAGEPOOLID`=2, `MKFILEMSG_FLAG_HAS_EVENT`=4. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileRespMsg.h

## Purpose
Defines `MkFileRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MkFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MkFileRespMsg` derives from `public NetMessageSerdes<MkFileRespMsg>` and uses `BaseType(NETMSGTYPE_MkFileResp)` or an equivalent base constructor. Constructors include `MkFileRespMsg(int result, EntryInfo* entryInfo) : BaseType(NETMSGTYPE_MkFileResp)`; `MkFileRespMsg() : BaseType(NETMSGTYPE_MkFileResp)`. Serialization writes `result`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`. Notable accessors/helpers include `getResult()`, `getEntryInfo()`. Declared payload/backing members include `int32_t result`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `MkFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileWithPatternMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileWithPatternMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileWithPatternRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileWithPatternRespMsg.h

## Purpose
Defines `MkFileWithPatternRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MkFileWithPatternResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MkFileWithPatternRespMsg` derives from `public NetMessageSerdes<MkFileWithPatternRespMsg>` and uses `BaseType(NETMSGTYPE_MkFileWithPatternResp)` or an equivalent base constructor. Constructors include `MkFileWithPatternRespMsg(int result, EntryInfo* entryInfo) : BaseType(NETMSGTYPE_MkFileWithPatternResp)`; `MkFileWithPatternRespMsg() : BaseType(NETMSGTYPE_MkFileWithPatternResp)`. Serialization writes `result`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`. Notable accessors/helpers include `getResult()`, `getEntryInfo()`. Declared payload/backing members include `int32_t result`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `MkFileWithPatternRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkFileWithPatternResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkFileWithPatternResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkFileWithPatternRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkLocalDirMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkLocalDirMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkLocalDirRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkLocalDirRespMsg.h

## Purpose
Defines `MkLocalDirRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MkLocalDirResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MkLocalDirRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_MkLocalDirResp)` or an equivalent base constructor. Constructors include `MkLocalDirRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_MkLocalDirResp, result)`; `MkLocalDirRespMsg() : SimpleIntMsg(NETMSGTYPE_MkLocalDirResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `MkLocalDirRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MkLocalDirResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MkLocalDirResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MkLocalDirRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MoveFileInodeMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MoveFileInodeMsg.h

## Purpose
Defines `MoveFileInodeMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_MoveFileInode`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`MoveFileInodeMsg` derives from `public MirroredMessageBase<MoveFileInodeMsg>` and uses `BaseType(NETMSGTYPE_MoveFileInode)` or an equivalent base constructor. Constructors include `MoveFileInodeMsg(EntryInfo* fromFileInfo, FileInodeMode mode, bool createLink = false) : BaseType(NETMSGTYPE_MoveFileInode), moveMode(mode), createHardlink(createLink), fromFileInfoPtr(fromFileInfo)`; `MoveFileInodeMsg(EntryInfo* fromFileInfo) : BaseType(NETMSGTYPE_MoveFileInode), moveMode(MODE_INVALID), fromFileInfoPtr(fromFileInfo)`; `MoveFileInodeMsg() : BaseType(NETMSGTYPE_MoveFileInode)`. Serialization writes `moveMode`, `createHardlink`, `backedPtr(obj->fromFileInfoPtr, obj->fromFileInfo)`. Notable accessors/helpers include `supportsMirroring()`, `getMode()`, `getCreateHardlink()`, `getFromFileEntryInfo()`. Declared payload/backing members include `int32_t moveMode`, `bool createHardlink`, `EntryInfo* fromFileInfoPtr`, `EntryInfo fromFileInfo`.

## Control Flow
Sender-side code builds `MoveFileInodeMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MoveFileInode`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MoveFileInode`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MoveFileInodeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MoveFileInodeRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MoveFileInodeRespMsg.h

## Purpose
Defines `MoveFileInodeRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_MoveFileInodeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`MoveFileInodeRespMsg` derives from `public NetMessageSerdes<MoveFileInodeRespMsg>` and uses `BaseType(NETMSGTYPE_MoveFileInodeResp)` or an equivalent base constructor. Constructors include `MoveFileInodeRespMsg(FhgfsOpsErr result, unsigned linkCount) : BaseType(NETMSGTYPE_MoveFileInodeResp)`; `MoveFileInodeRespMsg() : BaseType(NETMSGTYPE_MoveFileInodeResp)`. Serialization writes `result`, `linkCount`. Notable accessors/helpers include `getResult()`, `getHardlinkCount()`. Declared payload/backing members include `FhgfsOpsErr result`, `unsigned linkCount`.

## Control Flow
Sender-side code builds `MoveFileInodeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_MoveFileInodeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_MoveFileInodeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/MoveFileInodeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmChunkPathsMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmChunkPathsMsg.h

## Purpose
Defines `RmChunkPathsMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_RmChunkPaths`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RmChunkPathsMsg` derives from `public NetMessageSerdes<RmChunkPathsMsg>` and uses `BaseType(NETMSGTYPE_RmChunkPaths)` or an equivalent base constructor. Constructors include `RmChunkPathsMsg(uint16_t targetID, StringList* relativePaths) : BaseType(NETMSGTYPE_RmChunkPaths)`; `RmChunkPathsMsg() : BaseType(NETMSGTYPE_RmChunkPaths)`. Serialization writes `targetID`, `backedPtr(obj->relativePaths, obj->parsed.relativePaths)`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getTargetID()`, `getRelativePaths()`. Declared payload/backing members include `uint16_t targetID`, `StringList* relativePaths`, `StringList relativePaths`.

## Control Flow
Sender-side code builds `RmChunkPathsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmChunkPaths`. Feature flags: `RMCHUNKPATHSMSG_FLAG_BUDDYMIRROR`=1.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmChunkPaths`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmChunkPathsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmChunkPathsRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmChunkPathsRespMsg.h

## Purpose
Defines `RmChunkPathsRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_RmChunkPathsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RmChunkPathsRespMsg` derives from `public NetMessageSerdes<RmChunkPathsRespMsg>` and uses `BaseType(NETMSGTYPE_RmChunkPathsResp)` or an equivalent base constructor. Constructors include `RmChunkPathsRespMsg(StringList* failedPaths) : BaseType(NETMSGTYPE_RmChunkPathsResp)`; `RmChunkPathsRespMsg() : BaseType(NETMSGTYPE_RmChunkPathsResp)`. Serialization writes `backedPtr(obj->failedPaths, obj->parsed.failedPaths)`. Notable accessors/helpers include `getFailedPaths()`. Declared payload/backing members include `StringList* failedPaths`, `StringList failedPaths`.

## Control Flow
Sender-side code builds `RmChunkPathsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmChunkPathsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmChunkPathsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmChunkPathsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirEntryMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirEntryMsg.h

## Purpose
Defines `RmDirEntryMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_RmDirEntry`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RmDirEntryMsg` derives from `public NetMessageSerdes<RmDirEntryMsg>` and uses `BaseType(NETMSGTYPE_RmDirEntry)` or an equivalent base constructor. Constructors include `RmDirEntryMsg(EntryInfo* parentInfo, std::string& entryName) : BaseType(NETMSGTYPE_RmDirEntry), entryName(entryName)`; `RmDirEntryMsg() : BaseType(NETMSGTYPE_RmDirEntry)`. Serialization writes `backedPtr(obj->parentInfoPtr, obj->parentInfo)`, `stringAlign4(obj->entryName)`. Notable accessors/helpers include `getEntryName()`, `getParentInfo()`. Declared payload/backing members include `std::string entryName`, `EntryInfo* parentInfoPtr`, `EntryInfo parentInfo`.

## Control Flow
Sender-side code builds `RmDirEntryMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/Path.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmDirEntry`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmDirEntry`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirEntryMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirEntryRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirEntryRespMsg.h

## Purpose
Defines `RmDirEntryRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_RmDirEntryResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RmDirEntryRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RmDirEntryResp)` or an equivalent base constructor. Constructors include `RmDirEntryRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_RmDirEntryResp, result)`; `RmDirEntryRespMsg() : SimpleIntMsg(NETMSGTYPE_RmDirEntryResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RmDirEntryRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmDirEntryResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmDirEntryResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirEntryRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirMsg.h

## Purpose
Defines `RmDirMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_RmDir`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RmDirMsg` derives from `public MirroredMessageBase<RmDirMsg>` and uses `BaseType(NETMSGTYPE_RmDir)` or an equivalent base constructor. Constructors include `RmDirMsg(EntryInfo* parentInfo, std::string& delDirName) : BaseType(NETMSGTYPE_RmDir)`; `RmDirMsg() : BaseType(NETMSGTYPE_RmDir)`. Serialization writes `backedPtr(obj->parentInfoPtr, obj->parentInfo)`, `stringAlign4(obj->delDirName)`, `fileEvent`, `dirTimestamps`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getParentInfo()`, `getDelDirName()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `std::string delDirName`, `FileEvent fileEvent`, `EntryInfo* parentInfoPtr`, `EntryInfo parentInfo`, `MirroredTimestamps dirTimestamps`.

## Control Flow
Sender-side code builds `RmDirMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmDir`. Feature flags: `RMDIRMSG_FLAG_HAS_EVENT`=1. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmDir`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirRespMsg.h

## Purpose
Defines `RmDirRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_RmDirResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RmDirRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RmDirResp)` or an equivalent base constructor. Constructors include `RmDirRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_RmDirResp, result)`; `RmDirRespMsg() : SimpleIntMsg(NETMSGTYPE_RmDirResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RmDirRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmDirResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmDirResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmDirRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmLocalDirMsg.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmLocalDirMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmLocalDirRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmLocalDirRespMsg.h

## Purpose
Defines `RmLocalDirRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_RmLocalDirResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RmLocalDirRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_RmLocalDirResp)` or an equivalent base constructor. Constructors include `RmLocalDirRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_RmLocalDirResp, result)`; `RmLocalDirRespMsg() : SimpleIntMsg(NETMSGTYPE_RmLocalDirResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RmLocalDirRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmLocalDirResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmLocalDirResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmLocalDirRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkFileMsg.h

## Purpose
Defines `UnlinkFileMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_UnlinkFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UnlinkFileMsg` derives from `public MirroredMessageBase<UnlinkFileMsg>` and uses `BaseType(NETMSGTYPE_UnlinkFile)` or an equivalent base constructor. Constructors include `UnlinkFileMsg(EntryInfo* parentInfo, std::string& delFileName) : BaseType(NETMSGTYPE_UnlinkFile)`; `UnlinkFileMsg() : BaseType(NETMSGTYPE_UnlinkFile)`. Serialization writes `backedPtr(obj->parentInfoPtr, obj->parentInfo)`, `stringAlign4(obj->delFileName)`, `fileEvent`, `dirTimestamps`, `fileInfo`, `fileTimestamps`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `supportsMirroring()`, `getParentInfo()`, `getDelFileName()`, `getFileEvent()`, `getSupportedHeaderFeatureFlagsMask()`. Declared payload/backing members include `std::string delFileName`, `FileEvent fileEvent`, `EntryInfo* parentInfoPtr`, `EntryInfo parentInfo`, `MirroredTimestamps dirTimestamps`, `EntryInfo fileInfo`, `MirroredTimestamps fileTimestamps`.

## Control Flow
Sender-side code builds `UnlinkFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`, `common/storage/FileEvent.h`, `common/storage/Path.h`, `common/storage/StatData.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkFile`. Feature flags: `UNLINKFILEMSG_FLAG_HAS_EVENT`=1. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkFileRespMsg.h

## Purpose
Defines `UnlinkFileRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_UnlinkFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UnlinkFileRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_UnlinkFileResp)` or an equivalent base constructor. Constructors include `UnlinkFileRespMsg(int result) : SimpleIntMsg(NETMSGTYPE_UnlinkFileResp, result)`; `UnlinkFileRespMsg() : SimpleIntMsg(NETMSGTYPE_UnlinkFileResp)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `UnlinkFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileInodeMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileInodeMsg.h

## Purpose
Defines `UnlinkLocalFileInodeMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_UnlinkLocalFileInode`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UnlinkLocalFileInodeMsg` derives from `public MirroredMessageBase<UnlinkLocalFileInodeMsg>` and uses `BaseType(NETMSGTYPE_UnlinkLocalFileInode)` or an equivalent base constructor. Constructors include `UnlinkLocalFileInodeMsg(EntryInfo* delEntryInfo) : BaseType(NETMSGTYPE_UnlinkLocalFileInode), delEntryInfoPtr(delEntryInfo)`; `UnlinkLocalFileInodeMsg() : BaseType(NETMSGTYPE_UnlinkLocalFileInode)`. Serialization writes `backedPtr(obj->delEntryInfoPtr, obj->delEntryInfo)`. Notable accessors/helpers include `getDelEntryInfo()`, `supportsMirroring()`. Declared payload/backing members include `EntryInfo* delEntryInfoPtr`, `EntryInfo delEntryInfo`.

## Control Flow
Sender-side code builds `UnlinkLocalFileInodeMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkLocalFileInode`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; buddy-mirror forwarding requires the primary to fill replay-only fields correctly; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkLocalFileInode`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileInodeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileInodeRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileInodeRespMsg.h

## Purpose
Defines `UnlinkLocalFileInodeRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_UnlinkLocalFileInodeResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UnlinkLocalFileInodeRespMsg` derives from `public NetMessageSerdes<UnlinkLocalFileInodeRespMsg>` and uses `BaseType(NETMSGTYPE_UnlinkLocalFileInodeResp)` or an equivalent base constructor. Constructors include `UnlinkLocalFileInodeRespMsg(FhgfsOpsErr result, unsigned linkCount) : BaseType(NETMSGTYPE_UnlinkLocalFileInodeResp)`; `UnlinkLocalFileInodeRespMsg() : BaseType(NETMSGTYPE_UnlinkLocalFileInodeResp)`. Serialization writes `result`, `preUnlinkHardlinkCount`. Notable accessors/helpers include `getResult()`, `getPreUnlinkHardlinkCount()`. Declared payload/backing members include `FhgfsOpsErr result`, `unsigned preUnlinkHardlinkCount`.

## Control Flow
Sender-side code builds `UnlinkLocalFileInodeRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkLocalFileInodeResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkLocalFileInodeResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileInodeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileMsg.h

## Purpose
Defines `UnlinkLocalFileMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_UnlinkLocalFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UnlinkLocalFileMsg` derives from `public NetMessageSerdes<UnlinkLocalFileMsg>` and uses `BaseType(NETMSGTYPE_UnlinkLocalFile)` or an equivalent base constructor. Constructors include `UnlinkLocalFileMsg(std::string& entryID, uint16_t targetID, PathInfo* pathInfo) : BaseType(NETMSGTYPE_UnlinkLocalFile)`; `UnlinkLocalFileMsg() : BaseType(NETMSGTYPE_UnlinkLocalFile)`. Serialization writes `rawString(obj->entryID, obj->entryIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getEntryID()`, `getTargetID()`, `getPathInfo()`. Declared payload/backing members include `unsigned entryIDLen`, `const char* entryID`, `uint16_t targetID`, `PathInfo* pathInfoPtr`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `UnlinkLocalFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkLocalFile`. Feature flags: `UNLINKLOCALFILEMSG_FLAG_BUDDYMIRROR`=1, `UNLINKLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=2.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkLocalFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileRespMsg.h

## Purpose
Defines `UnlinkLocalFileRespMsg`, the response payload wrapper for BeeGFS namespace mutation RPCs using `NETMSGTYPE_UnlinkLocalFileResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`UnlinkLocalFileRespMsg` derives from `public SimpleIntMsg` and uses `BaseType(NETMSGTYPE_UnlinkLocalFileResp)` or an equivalent base constructor. Constructors include `UnlinkLocalFileRespMsg(FhgfsOpsErr result) : SimpleIntMsg(NETMSGTYPE_UnlinkLocalFileResp, result)`; `UnlinkLocalFileRespMsg() : SimpleIntMsg(NETMSGTYPE_UnlinkLocalFileResp)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getResult()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `UnlinkLocalFileRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/SimpleIntMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_UnlinkLocalFileResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UnlinkLocalFileResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/UnlinkLocalFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalMsg.h

## Purpose
Defines `ListChunkDirIncrementalMsg`, a BeeGFS directory and chunk listing query/request message using `NETMSGTYPE_ListChunkDirIncremental`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`ListChunkDirIncrementalMsg` derives from `public NetMessageSerdes<ListChunkDirIncrementalMsg>` and uses `BaseType(NETMSGTYPE_ListChunkDirIncremental)` or an equivalent base constructor. Constructors include `ListChunkDirIncrementalMsg(uint16_t targetID, bool isMirror, const std::string& relativeDir, int64_t offset, unsigned maxOutEntries, bool onlyFiles, bool ignoreNotExists) : BaseType(NETMSGTYPE_ListChunkDirIncremental), targetID(targetID), isMirror(isMirror), relativeDir(relativeDir), offset(offset), maxOutEntries(maxOutEntries), onlyFiles(onlyFiles), ignoreNotExists(ignoreNotExists)`; `ListChunkDirIncrementalMsg() : BaseType(NETMSGTYPE_ListChunkDirIncremental)`. Serialization writes `stringAlign4(obj->relativeDir)`, `targetID`, `isMirror`, `offset`, `maxOutEntries`, `onlyFiles`, `ignoreNotExists`. Notable accessors/helpers include `isMirror()`, `getTargetID()`, `getIsMirror()`, `getOffset()`, `getMaxOutEntries()`, `getRelativeDir()`, `getOnlyFiles()`, `getIgnoreNotExists()`. Declared payload/backing members include `uint16_t targetID`, `bool isMirror`, `std::string relativeDir`, `int64_t offset`, `uint32_t maxOutEntries`, `bool onlyFiles`, `bool ignoreNotExists`.

## Control Flow
Sender-side code builds `ListChunkDirIncrementalMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/message/storage/listing/ListChunkDirIncrementalRespMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the directory and chunk listing code path that handles `NETMSGTYPE_ListChunkDirIncremental`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; offset cursors can repeat or skip records if callers mishandle continuation.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListChunkDirIncremental`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalRespMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalRespMsg.h

## Purpose
Defines `ListChunkDirIncrementalRespMsg`, the response payload wrapper for BeeGFS directory and chunk listing RPCs using `NETMSGTYPE_ListChunkDirIncrementalResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`ListChunkDirIncrementalRespMsg` derives from `public NetMessageSerdes<ListChunkDirIncrementalRespMsg>` and uses `BaseType(NETMSGTYPE_ListChunkDirIncrementalResp)` or an equivalent base constructor. Constructors include `ListChunkDirIncrementalRespMsg(FhgfsOpsErr result, StringList* names, IntList* entryTypes, int64_t newOffset) : BaseType(NETMSGTYPE_ListChunkDirIncrementalResp)`; `ListChunkDirIncrementalRespMsg() : BaseType(NETMSGTYPE_ListChunkDirIncrementalResp)`. Serialization writes `result`, `newOffset`, `backedPtr(obj->names, obj->parsed.names)`, `backedPtr(obj->entryTypes, obj->parsed.entryTypes)`. Notable accessors/helpers include `getNames()`, `getEntryTypes()`, `getResult()`, `getNewOffset()`. Declared payload/backing members include `int32_t result`, `int64_t newOffset`, `StringList* names`, `IntList* entryTypes`, `StringList names`, `IntList entryTypes`.

## Control Flow
Sender-side code builds `ListChunkDirIncrementalRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the directory and chunk listing code path that handles `NETMSGTYPE_ListChunkDirIncrementalResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; offset cursors can repeat or skip records if callers mishandle continuation.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListChunkDirIncrementalResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListDirFromOffsetMsg.h -->
# sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListDirFromOffsetMsg.h

## Purpose
Defines `ListDirFromOffsetMsg`, a BeeGFS directory and chunk listing query/request message using `NETMSGTYPE_ListDirFromOffset`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`ListDirFromOffsetMsg` derives from `public NetMessageSerdes<ListDirFromOffsetMsg>` and uses `BaseType(NETMSGTYPE_ListDirFromOffset)` or an equivalent base constructor. Constructors include `ListDirFromOffsetMsg(EntryInfo* entryInfo, int64_t serverOffset, unsigned dirListLimit, bool filterDots) : BaseType(NETMSGTYPE_ListDirFromOffset)`; `ListDirFromOffsetMsg() : BaseType(NETMSGTYPE_ListDirFromOffset)`. Serialization writes `serverOffset`, `dirListLimit`, `backedPtr(obj->entryInfoPtr, obj->entryInfo)`, `filterDots`. Notable accessors/helpers include `getServerOffset()`, `getDirListLimit()`, `getEntryInfo()`, `getFilterDots()`. Declared payload/backing members include `int64_t serverOffset`, `uint32_t dirListLimit`, `bool filterDots`, `EntryInfo* entryInfoPtr`, `EntryInfo entryInfo`.

## Control Flow
Sender-side code builds `ListDirFromOffsetMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/EntryInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the directory and chunk listing code path that handles `NETMSGTYPE_ListDirFromOffset`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; offset cursors can repeat or skip records if callers mishandle continuation.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListDirFromOffset`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListDirFromOffsetMsg.h -->
