<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_linux.go -->
# sources/cloud-native/cri-o/server/container_remove_linux.go

## Purpose

This Linux-specific file closes seccomp notifiers when a container is removed.

## Important APIs, Types, and Functions

`removeSeccompNotifier(ctx, c)` loads a notifier from `s.seccompNotifiers` by container ID, type-asserts it to `*seccomp.Notifier`, and closes it.

## Control Flow

The function is called after container removal. If no notifier exists, it returns. If one exists and is the expected type, `Close` is called and close errors are logged.

## State and Persistence Behavior

It closes kernel/userland seccomp notification resources. The code does not delete the key from `seccompNotifiers`, so lifecycle assumptions depend on notifier close and broader server cleanup.

## Dependencies and Integration Points

It integrates with `setupSeccomp` in container creation, which stores notifiers in `s.seccompNotifiers`, and with the internal `config/seccomp.Notifier` type.

## Risks and Edge Cases

Type assertion failures are silently ignored. The map entry remaining after close could matter if container IDs were reused, though IDs should be unique.

## Test Signals

No direct tests are present for notifier cleanup. Removal tests exercise the caller but not this Linux-specific resource behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_linux.go -->
