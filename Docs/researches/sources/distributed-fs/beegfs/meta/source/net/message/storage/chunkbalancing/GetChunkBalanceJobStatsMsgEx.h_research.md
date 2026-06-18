<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h

Purpose: Declares the GetChunkBalanceJobStatsMsgEx server-side message extension: chunk-balancer query handler returning job statistics from the metadata node job registry.

Important APIs/types/functions: Declarations/types: class GetChunkBalanceJobStatsMsgEx : public GetChunkBalanceJobStatsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->
