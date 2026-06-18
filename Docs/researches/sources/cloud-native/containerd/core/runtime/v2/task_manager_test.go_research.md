# sources/cloud-native/containerd/core/runtime/v2/task_manager_test.go

## Purpose
Tests shim runtime path resolution for the task/shim manager.

## APIs, Flow, State, Dependencies, Risks, And Tests
`setupAbsoluteShimPath` creates an executable fake `containerd-shim-runc-v2` in a temp directory and prepends it to `PATH`. `TestResolveRuntimePath` checks absolute path resolution, runtime-name resolution through `exec.LookPath`, invalid absolute paths, empty names, relative paths, embedded slashes, and malformed runtime names.

State is limited to temp files and `PATH` environment mutation. The test depends on non-Windows/non-Darwin build tags and filesystem executable mode.

It guards against accepting unsafe relative shim paths and verifies expected runtime-name lookup. Gaps include cache invalidation behavior and side-by-side binary fallback via `os.Executable`.
