# sources/control-plane/longhorn-engine/pkg/sync/rpc/progress_tracker_test.go

Purpose: regression tests for per-file sync progress tracking during retry, ensuring rebuild/file-sync progress does not exceed 100%.

Important APIs/types/functions: `mockSyncOps` records cumulative processed bytes and computes percentage. Tests instantiate `perFileProgressOps`, call `UpdateSyncFileProgress`, and use `detach` to subtract failed-attempt contributions and ignore late callbacks.

Control flow: `TestProgressExceeds100WithoutTracker` documents the old bug where retrying a file adds bytes twice. `TestProgressStaysCorrectWithTracker` detaches after a partial attempt and verifies retry reaches exactly 100%. `TestProgressMultipleFilesWithRetry` simulates two files with one retry. `TestDetachIgnoresLateCallbacks` and `TestDetachIdempotent` verify detach semantics.

State and persistence: in-memory counters only.

Dependencies and integration points: tests `perFileProgressOps` from sync-agent server code, which wraps `sparserest.SyncFileOperations` callbacks during file sync/rebuild.

Risks: only single-threaded callback sequences are tested; concurrent progress callbacks could still need race testing. The mock uses integer percentage truncation, matching coarse status semantics but not byte-level API output.

Test signals: strong targeted regression signal for retry progress accounting and detach idempotence.
