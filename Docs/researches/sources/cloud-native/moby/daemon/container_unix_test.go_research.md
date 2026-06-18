# sources/cloud-native/moby/daemon/container_unix_test.go

## Purpose
Verifies that Unix daemon container settings validation warns when published ports are configured together with host network mode.

## Important APIs, Types, And Functions
- `TestContainerWarningHostAndPublishPorts` drives `verifyContainerSettings`.
- Test cases vary `HostConfig.NetworkMode` and `PortBindings`.

## Control Flow
Each subtest constructs a host config and empty container config, calls daemon validation, and compares returned warnings. Only the case with `NetworkMode: "host"` and non-empty port bindings should produce `Published ports are discarded when using host network mode`.

## State And Persistence
No daemon state is persisted. The daemon instance is empty and the config store is a test stub.

## Dependencies And Integration Points
Uses API container/network types and daemon validation helpers. The build tag restricts this test to Linux/FreeBSD where host network mode is supported.

## Risks And Edge Cases
This only validates warning emission, not the runtime discard behavior. It intentionally excludes Windows because host networking is unsupported there.

## Test Signals
Failures indicate user-facing warnings for ignored port publishing may be missing or emitted in the wrong cases.
