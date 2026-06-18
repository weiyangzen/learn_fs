# sources/cloud-native/containers-storage/pkg/system/stat_linux_test.go

Purpose: Linux-specific assertion helper for common stat conversion tests.

Important APIs/types/functions: `platformTestFromStatT(t, stat, s)` compares raw `Mode` and `Mtim` against `StatT`.

Control flow: called by `TestFromStatT` in `stat_unix_test.go`.

State/persistence: none.

Dependencies/integration: ties Linux syscall field names to the shared stat test.

Risks: narrowly checks only mode/time; size/dev coverage would need additional tests.

Test signals: catches regressions in Linux `fromStatT` time and mode field selection.
