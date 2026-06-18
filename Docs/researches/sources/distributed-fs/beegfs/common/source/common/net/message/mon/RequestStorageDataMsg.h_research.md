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
