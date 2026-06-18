# sources/cloud-native/containers-storage/pkg/system/syscall_windows_test.go

Purpose: smoke test for Windows win32k capability probing.

Important APIs/types/functions: `TestHasWin32KSupport`.

Control flow: calls `HasWin32KSupport` and logs the result without asserting a fixed value because host support varies.

State/persistence: none.

Dependencies/integration: exercises lazy API-set loading on Windows test hosts.

Risks: only verifies non-panic behavior, not semantic correctness.

Test signals: useful as a host-compatibility smoke test when Windows API-set availability changes.
