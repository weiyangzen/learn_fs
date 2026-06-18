# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameMsg.h

## Purpose
Defines `GetHostByNameMsg`, a BeeGFS helper daemon query/request message using `NETMSGTYPE_GetHostByName`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetHostByNameMsg` derives from `public NetMessageSerdes<GetHostByNameMsg>` and uses `BaseType(NETMSGTYPE_GetHostByName)` or an equivalent base constructor. Constructors include `GetHostByNameMsg(const char* hostname) : BaseType(NETMSGTYPE_GetHostByName)`; `GetHostByNameMsg() : BaseType(NETMSGTYPE_GetHostByName)`. Serialization writes `rawString(obj->hostname, obj->hostnameLen)`. Notable accessors/helpers include `getHostname()`. Declared payload/backing members include `unsigned hostnameLen`, `const char* hostname`.

## Control Flow
Sender-side code builds `GetHostByNameMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_GetHostByName`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetHostByName`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
