# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/pushpull.go

Purpose: implements `beegfs remote push` and `beegfs remote pull`, the front-end commands for scheduling upload/download Remote jobs.

Important APIs/types/functions: `pushPullCfg`; `newPushCmd`; `newPullCmd`; `runPushOrPullCmd`; `flex.JobRequestCfg`; hidden flags for force, metadata, tagging, and storage class; shared priority and update validation.

Control flow: each command builds a backend job request config, validates argument count and flag combinations, normalizes optional priority and allow-restore only when flags were explicitly changed, sets the path, then calls `rst.SubmitJobRequest` with a buffer of 1024. The runner drains asynchronous responses, handles fatal vs non-fatal errors, updates counters by `SubmitJobResponse` status, prints detailed job rows only in verbose/debug except for not-allowed failures, and returns partial success when any job could not start or a previous failed job blocks scheduling.

State and persistence: schedules remote synchronization jobs and may update persistent file RST configuration when `--update` is used. `push --stub-local` can replace uploaded files with stubs; `pull` may overwrite local contents, create stubs, flatten paths, or restore archived requests.

Dependencies and integration points: integrates Cobra flags, common filesystem filters, common/RST flag names and validation, BeeRemote protobuf statuses, `newJobsTable`, `cmdfmt.Printf`, Viper global flags, and CTL exit-code wrapping.

Risks: hidden force and metadata/tagging/storage-class flags can materially change behavior while being less visible. Tagging is manually joined as `key=value&...` without URL escaping here, so backend expectations matter. `--update` requires a valid remote target but only validates nonzero via common RST validation. Partial success is communicated through an error containing the formatted summary.

Test signals: no direct tests. Key test cases include invalid priority, update without target, fatal response early flush, ignored no-RST/unsupported files, status counter totals, verbose/debug row choices, and disabled-emoji summary text.
