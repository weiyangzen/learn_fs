# sources/cloud-native/cri-o/internal/watchdog/watchdog_test_inject.go

Purpose: test-only injection hook for replacing the watchdog's systemd implementation.

Important APIs/types/functions: `SetSystemd(systemd Systemd)` mutates `w.systemd`.

Control flow: no branching; direct field assignment.

State and persistence: mutates in-memory `Watchdog` state for tests only.

Dependencies/integration: guarded by `//go:build test`, used by `watchdog_test.go` to inject gomock `Systemd`.

Risks: must only be available in test builds; exposing it in production would allow uncontrolled replacement of the notification backend.

Test signals: package tests depend on this method to avoid real systemd calls.
