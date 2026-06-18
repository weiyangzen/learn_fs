<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_posix_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_posix_test.go

Purpose: POSIX-oriented test coverage for hardlink ordering in exported change archives.

Important APIs/types/functions: `TestHardLinkOrder`, `tarHeaders`, and `walkHeaders`. The test builds a source tree, copies it, creates multiple hardlinks for each file in the destination, calls `ChangesDirs`, and exports the same changes in forward and reverse order.

Control flow: after building hardlinks, the test sorts changes ascending, exports headers, sorts changes descending, exports headers again, sorts both header lists by name, and compares name, size, type, and link target. Solaris is skipped because the copy helper is unreliable there.

State/persistence: uses temporary directories and hardlinks only. No durable state remains after test cleanup.

Dependencies/integration: validates `ChangesDirs`, `ExportChanges`, hardlink detection, and tar header generation from the archive package.

Risks/test signal: this specifically protects deterministic hardlink archive semantics: export order must not change whether an entry is emitted as file content or hardlink metadata. Regressions would produce archives that unpack differently depending on change ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_posix_test.go -->
