
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/quota/quota.go

- Purpose: implements quota management for pool defaults, explicit limits, and usage reporting.
- Important APIs: `NewCmd`, `newListCmd`, `newSetDefaultCmd`, `newSetLimitsCmd`, `runSetLimitsCmd`, `newListLimitsCmd`, `runListLimitsCmd`, `newListUsageCmd`, `runListUsageCmd`, `parseLimit`, `parseUserIdsInto`, `parseGroupIdsInto`, `getCurrentGroupIds`, and `idToName`.
- Control flow/state: builds quota protobuf requests, expands user/group ID ranges into individual `QuotaInfo` entries for set-limits, streams limits/usage responses, formats raw or human-readable values, and restricts arbitrary ID queries to root.
- Dependencies/integration: uses pool listing for defaults, quota backend streams, management protobuf builders, OS user/group lookup, and CTL formatting utilities.
- Risks/tests: large ID ranges can generate huge request slices; `unlimited` maps to `MaxInt64` while usage displays `-1` as unlimited. No direct tests.
