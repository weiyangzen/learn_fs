
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/job.go

- Purpose: implements Remote Storage Target job management: cancel, cleanup, cleanup orphaned via registered subcommand, and list.
- Important APIs: `newJobCmd`, `newCancelCmd`, `newCleanupCmd`, `updateJobRunner`, `listJobsConfig`, `newListJobsCmd`, and `runListJobsCmd`.
- Control flow/state: cancel/cleanup build `rst.UpdateJobCfg` with target state, gate recursive updates with `--yes`, stream update responses into job tables, return partial success when any update is not OK, and list jobs grouped by path/RST with table or retro verbose output.
- Dependencies/integration: uses filesystem path initialization, RST backend update/list streams, beeremote protobuf job/work states, job table helpers, Viper debug mode, and CTL partial-success errors.
- Risks/tests: recursive operations are database-prefix based, not live filesystem traversal; force cancellation deliberately ignores some backend errors to drive cleanup. No direct tests found.
