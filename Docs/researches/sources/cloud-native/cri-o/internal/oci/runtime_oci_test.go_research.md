# sources/cloud-native/cri-o/internal/oci/runtime_oci_test.go

## Purpose
Tests critical `runtimeOCI` stop/status utility behavior using mocked command runners and real short-lived processes.

## Test Signals
Stop-loop tests verify early return when runtime kill fails but the process is already gone, graceful stop before timeout, SIGKILL fallback after timeout, shorter timeout updates overriding longer waits, longer updates not extending an earlier target, many concurrent timeout updates, and context cancellation. `TruncateAndReadFile` tests validate size-capped reads. `UpdateContainerStatus` tests verify fast-exit race handling: wait for `dir/exit` and read code 0 instead of immediately defaulting to 255; also verify default 255 when no exit file appears.

## Dependencies and Risks
Uses mock `cmdrunner`, temporary attach/socket/container dirs, actual `sleep` processes, and test-only `RuntimeOCI`. These tests strongly cover concurrency timing but remain sensitive to host process and timer behavior.
