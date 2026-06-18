<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_unix_test.go

Purpose: Unix helper for tests that need stable symlink timestamps.

Important APIs/types/functions: `resetSymlinkTimes`.

Control flow: creates two zero `unix.Timeval` values and calls `unix.Lutimes` so the symlink itself, not its target, has deterministic atime/mtime.

State/persistence: mutates temporary test symlink metadata only.

Dependencies/integration: used by `createSampleDir` and mutation tests in `changes_test.go` to make symlink target changes visible even when length and timestamp would otherwise be ambiguous.

Risks/test signal: if `Lutimes` behavior varies by filesystem/platform, symlink change tests may become flaky. The helper is Unix-only; Windows uses a no-op variant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_unix_test.go -->
