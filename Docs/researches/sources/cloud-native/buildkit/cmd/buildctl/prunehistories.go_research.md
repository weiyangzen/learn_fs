# Research: sources/cloud-native/buildkit/cmd/buildctl/prunehistories.go

Purpose: implements `buildctl prune-histories`, which deletes unpinned build history records and prints the records it removed.

Important APIs and flow: `pruneHistories` resolves the client, opens a `ListenBuildHistory` stream with `EarlyExit`, then either templates each deleted event or delegates to `pruneHistoriesWithTableOutput`. Both modes skip nil and pinned records, call `UpdateBuildHistory(Delete: true)` for each remaining ref, collect deletion errors, and continue processing other records.

State and dependencies: mutates daemon history DB through the control API. It depends on app context, control API stream/update calls, common template parsing, tabwriter, local timestamp formatting, and joined errors.

Risks and test signals: the command is destructive for unpinned histories and has no confirmation. It intentionally aggregates per-record errors. There are no direct tests in this subset; behavior overlaps with debug history APIs and daemon history queue logic.
