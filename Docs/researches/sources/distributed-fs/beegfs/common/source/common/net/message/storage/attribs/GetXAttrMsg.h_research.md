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
