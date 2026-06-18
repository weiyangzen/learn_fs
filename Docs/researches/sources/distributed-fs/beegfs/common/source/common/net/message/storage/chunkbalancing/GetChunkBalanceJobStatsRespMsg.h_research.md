# sources/distributed-fs/beegfs/common/source/common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsRespMsg.h

## Purpose
Defines `GetChunkBalanceJobStatsRespMsg`, the response payload wrapper for BeeGFS chunk balancing RPCs using `NETMSGTYPE_GetChunkBalanceJobStatsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetChunkBalanceJobStatsRespMsg` derives from `public NetMessageSerdes<GetChunkBalanceJobStatsRespMsg>` and uses `BaseType(NETMSGTYPE_GetChunkBalanceJobStatsResp)` or an equivalent base constructor. Constructors include `GetChunkBalanceJobStatsRespMsg(ChunkBalancerJobStatistics* jobStats) : BaseType(NETMSGTYPE_GetChunkBalanceJobStatsResp), jobStatsPtr(jobStats)`; `GetChunkBalanceJobStatsRespMsg() : BaseType(NETMSGTYPE_GetChunkBalanceJobStatsResp)`. Serialization writes `backedPtr(obj->jobStatsPtr, obj->jobStats)`. Notable accessors/helpers include `getJobStats()`. Declared payload/backing members include `ChunkBalancerJobStatistics* jobStatsPtr`, `ChunkBalancerJobStatistics jobStats`.

## Control Flow
Sender-side code builds `GetChunkBalanceJobStatsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/chunkbalancer/ChunkBalancerJobStatistics.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the chunk balancing code path that handles `NETMSGTYPE_GetChunkBalanceJobStatsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetChunkBalanceJobStatsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
