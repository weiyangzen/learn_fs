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
