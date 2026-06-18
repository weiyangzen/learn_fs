# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/StorageBenchControlMsg.h

## Purpose
Defines `StorageBenchControlMsg`, a BeeGFS node and target management command message using `NETMSGTYPE_StorageBenchControlMsg`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`StorageBenchControlMsg` derives from `public NetMessageSerdes<StorageBenchControlMsg>` and uses `BaseType(NETMSGTYPE_StorageBenchControlMsg)` or an equivalent base constructor. Constructors include `StorageBenchControlMsg(StorageBenchAction action, StorageBenchType type, int64_t blocksize, int64_t size, int threads, bool odirect, UInt16List* targetIDs) : BaseType(NETMSGTYPE_StorageBenchControlMsg)`; `StorageBenchControlMsg() : BaseType(NETMSGTYPE_StorageBenchControlMsg)`. Serialization writes `action`, `type`, `blocksize`, `size`, `threads`, `odirect`, `backedPtr(obj->targetIDs, obj->parsed.targetIDs)`. Notable accessors/helpers include `getAction()`, `getType()`, `getBlocksize()`, `getSize()`, `getThreads()`, `getODirect()`, `getTargetIDs()`. Declared payload/backing members include `int32_t action`, `int32_t type`, `int64_t blocksize`, `int64_t size`, `int32_t threads`, `bool odirect`, `UInt16List* targetIDs`, `UInt16List targetIDs`.

## Control Flow
Sender-side code builds `StorageBenchControlMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/benchmark/StorageBench.h`, `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_StorageBenchControlMsg`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StorageBenchControlMsg`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
