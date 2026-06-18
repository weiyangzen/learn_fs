
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/stats.go

- Purpose: prints resync statistics for a buddy group.
- Important APIs: `newResyncStatsCmd`, `runResyncStatsCmd`, `printMetaResults`, and `printStorageResults`.
- Control flow/state: parses a group ID, resolves the current primary with `backend.GetPrimaryTarget`, dispatches to metadata or storage stats RPC based on node type, then prints candidate, error, progress, and result counters.
- Dependencies/integration: depends on BeeMsg response types, entity parsing, and resync backend helpers.
- Risks/tests: direct `fmt` output is not table-aware; output field coverage must track protocol changes. No local tests in this file.
