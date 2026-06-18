# sources/distributed-fs/beegfs/common/source/common/net/message/helperd/LogMsg.h

## Purpose
Defines `LogMsg`, a BeeGFS helper daemon command message using `NETMSGTYPE_Log`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`LogMsg` derives from `public NetMessageSerdes<LogMsg>` and uses `BaseType(NETMSGTYPE_Log)` or an equivalent base constructor. Constructors include `LogMsg(int level, int threadID, const char* threadName, const char* context, const char* logMsg) : BaseType(NETMSGTYPE_Log)`; `LogMsg() : BaseType(NETMSGTYPE_Log)`. Serialization writes `level`, `threadID`, `rawString(obj->threadName, obj->threadNameLen)`, `rawString(obj->context, obj->contextLen)`, `rawString(obj->logMsg, obj->logMsgLen)`. Notable accessors/helpers include `getLevel()`, `getThreadID()`, `getThreadName()`, `getContext()`, `getLogMsg()`. Declared payload/backing members include `int32_t level`, `int32_t threadID`, `unsigned threadNameLen`, `const char* threadName`, `unsigned contextLen`, `const char* context`, `unsigned logMsgLen`, `const char* logMsg`.

## Control Flow
Sender-side code builds `LogMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the helper daemon code path that handles `NETMSGTYPE_Log`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_Log`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
