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
