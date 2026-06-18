# sources/cloud-native/containerd/internal/cri/server/podsandbox/controller.go

## Purpose

This file registers the `podsandbox` sandbox controller plugin and defines the controller's core state and event-wait behavior for pause-container-backed Kubernetes pod sandboxes. It is the bridge between containerd's generic `sandbox.Controller` interface and CRI's pod sandbox metadata, store, warning, and event-monitor facilities.

## Important APIs, Types, and Functions

`Controller` holds CRI runtime/image config, a containerd client, warning service, OS abstraction, pod sandbox event monitor, and an in-memory `Store`. `init` registers the plugin with event, lease, sandbox-store, transfer, CRI, service, and warning dependencies. `Platform` returns the default OCI platform. `Wait` waits on a cached `types.PodSandbox`. `Update` is currently a no-op. `waitSandboxExit` converts a task wait result into a `TaskExit` event. `handleSandboxTaskExit` deletes the pause task and marks the sandbox exited.

## Control Flow

Plugin initialization builds an in-memory-services client, retrieves CRI runtime and image service configs, creates the controller, starts an event monitor, and returns the controller. Runtime exit handling waits on the task channel, converts failures to exit code 255, applies a timeout for delete/status mutation, and uses event-monitor backoff when cleanup fails.

## State and Persistence Behavior

The controller stores live pod sandbox objects only in memory. Durable metadata is carried elsewhere in containerd sandbox/container extensions. Exit handling mutates the sandbox status to not-ready and releases waiters through the `PodSandbox` stop channel.

## Dependencies and Integration Points

It integrates with containerd plugin registration, CRI service plugins, the warning service, `events.EventMonitor`, `containerd.Task` deletion, protobuf timestamp conversion, and the pod sandbox store types.

## Risks and Test Signals

Risks include missed cleanup if the in-memory store lacks an entry, blocked serialized event handling, and current `Update` no-op behavior. Controller tests cover basic status access; broader signals come from sandbox lifecycle, recovery, and event monitor integration tests.
