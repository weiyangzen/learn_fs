# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RefreshTargetStatesMsg.h

## Purpose
Defines `RefreshTargetStatesMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RefreshTargetStates`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RefreshTargetStatesMsg` derives from `public AcknowledgeableMsgSerdes<RefreshTargetStatesMsg>` and uses `BaseType(NETMSGTYPE_RefreshTargetStates)` or an equivalent base constructor. Constructors include `RefreshTargetStatesMsg() : BaseType(NETMSGTYPE_RefreshTargetStates)`. Payload serialization is empty or delegated to an inherited helper type. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `RefreshTargetStatesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RefreshTargetStates`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RefreshTargetStates`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
