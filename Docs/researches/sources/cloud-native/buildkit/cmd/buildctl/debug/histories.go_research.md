# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/histories.go

Purpose: implements `buildctl debug histories`, a read-only command for listing build history records from the daemon.

Important APIs and flow: `histories` resolves the client, calls `ListenBuildHistory` with `EarlyExit`, and either applies a user template to each event or prints a tabular stream via `printRecordsTable`. The table includes event type, ref, created/completed timestamps, generation, and a pinned marker.

State and dependencies: reads daemon history DB through the control API. It depends on common template parsing, app context, control API stream clients, `io.EOF` handling, tabwriter, and local timezone formatting.

Risks and test signals: template mode exposes raw events while table mode only shows selected fields. Streaming errors abort output. Direct tests are absent, but `prune-histories` uses similar stream handling.
