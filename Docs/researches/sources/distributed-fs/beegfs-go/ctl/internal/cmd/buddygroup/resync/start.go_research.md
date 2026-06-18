
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/start.go

- Purpose: implements `mirror resync start <buddy-group>` for metadata or storage mirror resync.
- Important APIs: `startResync_config`, `newStartResyncCmd`, and `runStartResyncCmd`.
- Control flow/state: parses group ID, supports `--timestamp` or `--timespan`; timespan converts to Unix timestamp using current time, then calls `backend.StartResync` with a restart flag.
- Dependencies/integration: uses BeeGFS entity parsing and `ctl/pkg/ctl/buddygroup/resync`.
- Risks/tests: timestamp and timespan cannot both be set, and timespan is storage-only by help text but not visibly enforced here. No direct tests found.
