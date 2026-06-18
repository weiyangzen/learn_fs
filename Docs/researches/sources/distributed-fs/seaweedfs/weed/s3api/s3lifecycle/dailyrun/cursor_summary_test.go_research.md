# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_summary_test.go

Purpose: tests operator-facing summary output for daily-run cursor lag and walker freshness.

Important APIs/types: exercises `summarizeShardCursorLag` using `memPersister` and `Config.Shards`.

Control flow: tests cover all-cold-start output, worst-shard max selection, and partial cursor/walker populations. Assertions verify stable key tokens such as `cursor_lag_max=` and `walked_max_age=`.

State and persistence behavior: uses in-memory cursor persistence. It validates how persisted `TsNs` and `LastWalkedNs` are interpreted for heartbeat logs.

Dependencies and integration points: tied to `Run`'s final log line, which operator scripts and CI greps parse.

Risks: summary ignores load errors and missing cursors; tests document this by expecting cold markers only when no saved values exist. It does not test negative lag from future cursor timestamps.

Test signals: good coverage for observability semantics, especially distinguishing cold start from zero lag.
