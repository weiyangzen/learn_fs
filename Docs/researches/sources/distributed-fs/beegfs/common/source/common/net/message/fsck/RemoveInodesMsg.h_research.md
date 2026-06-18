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
