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
