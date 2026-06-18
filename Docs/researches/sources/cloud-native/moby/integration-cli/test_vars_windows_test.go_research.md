## sources/cloud-native/moby/integration-cli/test_vars_windows_test.go

Purpose: Windows build constants for integration CLI tests. It sets `isUnixCli = false` and uses Windows expected chmod rendering `"-rwxr-xr-x"` for historical compatibility.

Control flow and state are compile-time only. Dependencies are Windows build selection and shared tests that use `UnixCli` or `expectedFileChmod`.

Risks include stale permission expectation if Windows CLI output changes. Test signals are indirect through platform-conditional assertions in shared test files.
