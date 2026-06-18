# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/RegisterTargetMsg.h

## Purpose
Defines `RegisterTargetMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_RegisterTarget`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RegisterTargetMsg` derives from `public NetMessageSerdes<RegisterTargetMsg>` and uses `BaseType(NETMSGTYPE_RegisterTarget)` or an equivalent base constructor. Constructors include `RegisterTargetMsg(const char* targetID, uint16_t targetNumID) : BaseType(NETMSGTYPE_RegisterTarget)`; `RegisterTargetMsg() : BaseType(NETMSGTYPE_RegisterTarget)`. Serialization writes `rawString(obj->targetID, obj->targetIDLen)`, `targetNumID`. Notable accessors/helpers include `getTargetID()`, `getTargetNumID()`. Declared payload/backing members include `unsigned targetIDLen`, `const char* targetID`, `uint16_t targetNumID`.

## Control Flow
Sender-side code builds `RegisterTargetMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/sock/NetworkInterfaceCard.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_RegisterTarget`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RegisterTarget`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
