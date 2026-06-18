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
