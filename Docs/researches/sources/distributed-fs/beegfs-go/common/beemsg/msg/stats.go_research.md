<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/stats.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/stats.go

Purpose: BeeMsg definitions for high-resolution server stats, client stats v1/v2, and dummy metadata/storage requests used to detect client-stats version support.

Important APIs/types/functions: `GetHighResStats`, `GetHighResStatsResp`, `HighResolutionStats`, `GetClientStats`, `GetClientStatsResp`, `Uint128`, `GetClientStatsV2`, `GetClientStatsV2Resp`, `RequestMetaData`, `RequestMetaDataRespDummy`, `RequestStorageData`, and `RequestStorageDataRespDummy`.

Control flow: request serializers write last-stat times, cookies, or `Uint128` low/high halves. `PerUser` sets message feature flag 1. Response deserializers read sequences; dummy deserializers only inspect feature flag 1 and reset the buffer so unprocessed response content is ignored.

State and persistence: no persistence; stats structs are remote snapshots. `UseClientStatsV2` is inferred from response header feature flags rather than body fields.

Dependencies and integration points: depends on `beeserde` sequence helpers and header feature-flag propagation from `DisassembleBeeMsg`. These messages integrate with management/monitoring paths selecting stats protocol versions.

Risks: dummy response types intentionally discard bodies, so they only remain valid while the caller truly needs feature flags only. `Uint128` field ordering differs from serialized order in comments/code: serializer writes Low then High and deserializer reads Low then High.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/stats.go -->
