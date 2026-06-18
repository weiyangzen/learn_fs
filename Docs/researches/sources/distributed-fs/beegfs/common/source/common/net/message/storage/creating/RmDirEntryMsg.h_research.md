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
