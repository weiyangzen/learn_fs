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
