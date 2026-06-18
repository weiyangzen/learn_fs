<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util_test.go -->
# sources/control-plane/csi-driver-smb/pkg/util/util_test.go

Purpose: Unit tests for utility timeout behavior and case-insensitive map insertion.

Important APIs/functions: `TestWaitUntilTimeout` exercises `WaitUntilTimeout` when `execFunc` returns an error, exceeds the timeout, and completes successfully. It uses `go.uber.org/goleak` to detect leaked goroutines after delayed timeout cleanup. `TestSetKeyValueInMap` mirrors the SMB package helper tests for nil maps, new keys, existing keys, and case-insensitive replacement.

Control flow: Timeout test cases run callbacks with one-second timeouts; when an error occurs, the test sleeps to let slow goroutines finish before goleak verification.

State and persistence behavior: No filesystem persistence. Tests rely on goroutine scheduling and wall-clock sleep.

Dependencies and integration points: The timeout behavior is important for node SMB mounts, where the timeout reports failure but cannot cancel the mount operation.

Risks: Wall-clock sleeps can make the test suite slower and potentially flaky under extreme load. The test does not cover `RunPowershellCmd`, likely because it is Windows/environment dependent.

Test signals: Good signal for callback return selection and absence of permanent goroutine leaks; limited signal for command execution utilities.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util_test.go -->
