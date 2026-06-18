
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/restart.go

- Purpose: defines `mirror resync restart <buddy-group>` as a restart variant of resync start.
- Important APIs: `newRestartCmd` reuses `startResync_config` and `runStartResyncCmd`.
- Control flow/state: parses a meta/storage buddy group, accepts `--timestamp` or `--timespan`, sets `restart: true`, and delegates execution to the shared start runner.
- Dependencies/integration: depends on `beegfs.NewEntityIdParser`, Cobra duration/int flags, and backend resync start semantics.
- Risks/tests: restart mode likely resets existing resync progress; validation for mutually exclusive timestamp/timespan is handled in shared code. No direct tests found.
