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
