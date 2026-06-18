<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug_test.go -->
# sources/cloud-native/moby/daemon/command/debug/debug_test.go

## Purpose
Tests the debug package's environment and logging side effects.

## Important APIs, Types, And Functions
`TestEnable`, `TestDisable`, and `TestEnabled` call `Enable`, `Disable`, `IsEnabled`, `os.Getenv`, and `log.GetLevel`.

## Control Flow
Tests toggle debug mode and assert the immediate process-level result. `TestEnable` registers cleanup to restore `DEBUG` and info log level.

## State And Persistence Behavior
Mutates process environment and global log level during test execution. Cleanup is important because later tests share the process.

## Dependencies And Integration Points
Depends on containerd logging. It verifies that the debug helper remains aligned with the logger used by daemon command code.

## Risks And Test Signals
Signals are exact `DEBUG=1`, empty `DEBUG` after disable, debug/info log levels, and `IsEnabled` returning true only for non-empty env state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug_test.go -->
