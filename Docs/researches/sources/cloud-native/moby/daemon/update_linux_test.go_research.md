# sources/cloud-native/moby/daemon/update_linux_test.go

## Purpose
Linux unit coverage for default resource update conversion.

## Important APIs, Types, And Functions
`TestToContainerdResources_Defaults` calls `toContainerdResources(container.Resources{})` and validates the result with `checkResourcesAreUnset`.

## Control Flow
The test creates an empty Docker API resource config, invokes the Linux converter, fails on unexpected conversion errors, then asserts that no cgroup resource values are set in the returned containerd resources.

## State And Persistence
No state is persisted; this is pure conversion validation.

## Dependencies And Integration Points
Depends on the daemon resource conversion function, Docker API resource type, and a test helper that checks unset resource semantics.

## Risks
The test covers only the empty/default case. It does not exercise blkio conversions, `NanoCPUs` quota math, CPU shares/cpuset, memory, swap, or pids behavior.

## Test Signals
The important signal is regression protection for nil/zero semantics: default Docker update input must not produce populated containerd resource fields that could reset runtime settings.
