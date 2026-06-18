<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_windows_test.go

Purpose: Windows test shim for symlink timestamp reset.

Important APIs/types/functions: `resetSymlinkTimes`.

Control flow: returns nil without modifying filesystem metadata.

State/persistence: none.

Dependencies/integration: satisfies the helper used by shared `changes_test.go` on Windows, where the symlink-heavy tests are mostly skipped.

Risks/test signal: the no-op means shared tests cannot assert symlink timestamp-sensitive behavior on Windows. This file is a portability shim, not substantive behavior coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows_test.go -->
