<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_test.go -->
# sources/cloud-native/buildkit/session/filesync/filesync_test.go

Purpose: tests selected filesync behaviors.

Important APIs, types, and functions: `TestFileSyncIncludePatterns` creates a temp source with `foo` and `bar`, attaches a filesystem provider, runs a session, calls `FSSync` with include pattern `ba*`, and verifies only `bar` is copied. `TestLocalExporterModeDeleteRequiresDaemonSupport` creates a delete-mode sync target without support metadata, expects an error, and verifies stale file content remains. `testFileSendStream` is a minimal stream stub returning EOF.

Control flow and state: uses temp directories and errgroup-managed session/caller concurrency. Tests explicitly close the session after sync.

Dependencies and integration: exercises `session`, `testutil`, fsutil FS, gRPC metadata, and local exporter target code.

Risks and test signals: covers important gates but not exclude/follow path combinations, non-ASCII metadata encoding, successful delete mode, or CopyFileWriter streaming.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_test.go -->
