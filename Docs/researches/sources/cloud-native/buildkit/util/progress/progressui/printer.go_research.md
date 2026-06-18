<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/printer.go -->
# sources/cloud-native/buildkit/util/progress/progressui/printer.go

Purpose: implements the plain text multiplexer used by progress UI plain mode. It serializes vertex transitions, status updates, warnings, logs, and completion markers into a stable human-readable stream.

Important APIs and types: `textMux.printVtx`, `textMux.print`, `sortCompleted`, `lastStatus`, `limitString`, and constants controlling anti-flicker and progress throttling. It operates on the `trace` and `vertex` types defined in `display.go`.

Control flow: `printVtx` assigns numeric vertex indexes, emits a header when switching active vertices, flushes pending events, prints status deltas only when progress/time thresholds warrant, emits new warnings, writes log lines with vertex prefixes, and prints terminal state (`DONE`, `CACHED`, `ERROR`, or `CANCELED`) when a vertex is complete and has no open status. `print` decides which changed/completed vertices to emit first and uses `sortCompleted` for deterministic completion ordering.

State and persistence: `textMux` tracks the current digest, last status progress by status ID, whether the initial description has been printed, and the next display index. Vertices retain log offsets, ring buffers for last logs, warning indexes, event lists, and counts.

Dependencies and integration: depends on OCI digest keys, `units.Bytes`, environment variable `PROGRESS_NO_TRUNC`, and the trace model from `display.go`. It is created by `newPlainDisplay`.

Risks: throttling can defer status lines until either enough time or enough progress has elapsed. Status IDs are tracked globally in `textMux.last`, so non-unique IDs across vertices could affect anti-flicker behavior. The log ring stores only recent log lines for error replay in plain mode.

Test signals: no direct tests for text formatting; `display_test.go` covers interval merging used by completion duration summaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/printer.go -->
