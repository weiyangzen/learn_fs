# sources/cloud-native/moby/daemon/logger/loggerutils/file_windows_test.go

Purpose: Windows-specific tests for file helper semantics.

Important APIs/types/functions: `TestOpenFileDelete`, `TestOpenFileRename`, and `TestUnlinkOpenFile`.

Control flow/state/persistence: tests create temporary files, hold handles open, and verify delete/rename/unlink behavior succeeds with the helper's share flags.

Dependencies/integration: validates the Windows platform layer needed by `LogFile` rotation.

Risks: Windows-only coverage; failures here usually indicate rotation regressions on Windows.

Test signals: direct signal for delete/rename compatibility with active readers.
