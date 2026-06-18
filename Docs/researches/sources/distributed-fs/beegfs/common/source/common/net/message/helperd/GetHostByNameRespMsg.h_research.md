# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/GetHostByNameRespMsg.h

## Purpose
Defines `GetHostByNameRespMsg`, the response payload wrapper for BeeGFS helper daemon RPCs using `NETMSGTYPE_GetHostByNameResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetHostByNameRespMsg` derives from `public NetMessageSerdes<GetHostByNameRespMsg>` and uses `BaseType(NETMSGTYPE_GetHostByNameResp)` or an equivalent base constructor. Constructors include `GetHostByNameRespMsg(const char* hostAddr) : BaseType(NETMSGTYPE_GetHostByNameResp)`; `GetHostByNameRespMsg() : BaseType(NETMSGTYPE_GetHostByNameResp)`. Serialization writes `rawString(obj->hostAddr, obj->hostAddrLen)`. Notable accessors/helpers include `getHostAddr()`. Declared payload/backing members include `unsigned hostAddrLen`, `const char* hostAddr`.

## Control Flow
Sender-side code builds `GetHostByNameRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_GetHostByNameResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetHostByNameResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
