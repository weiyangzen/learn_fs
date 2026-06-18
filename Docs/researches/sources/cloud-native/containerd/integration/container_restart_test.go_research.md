# sources/cloud-native/containerd/integration/container_restart_test.go

## Purpose

This file verifies basic CRI restart workflows for normal containers and containers that failed to start. It ensures a stopped/removed container can be recreated with the same metadata in the same sandbox.

## Important APIs, Types, And Functions

- `TestContainerRestart` starts a Pause container, stops/removes it, recreates it with the same config, and starts it again.
- `TestFailedContainerRestart` creates a bad-command container, expects start failure, removes it, then creates a valid replacement.
- Shared helper APIs provide sandbox/container config construction and cleanup.

## Control Flow

Both tests create a sandbox, ensure the Pause image exists, build a `ContainerConfig`, and call CRI `CreateContainer`/`StartContainer`. The successful restart path explicitly stops and removes the first container before recreating. The failed-start path expects `StartContainer` to fail, then still calls stop/remove before recreating with a corrected config.

## State And Persistence Behavior

The tests exercise CRI metadata cleanup and name reuse inside a sandbox. The key state transition is from created/running or created/failed to removed, followed by a new container record with the same name.

## Dependencies And Integration Points

They depend on CRI runtime lifecycle calls, the image helper package, and containerd metadata cleanup. They integrate with name uniqueness handling because reuse must only succeed after removal.

## Risks And Edge Cases

The failed-start test defers `StopContainer` even after a failed start; this is tolerated by the integration helper expectations but could hide differences in runtime handling of stopped/non-started containers. The tests do not inspect old task or snapshot cleanup directly.

## Test Signals

Passing shows that container metadata and runtime state are clean enough after normal removal and failed starts to allow same-name recreation.
