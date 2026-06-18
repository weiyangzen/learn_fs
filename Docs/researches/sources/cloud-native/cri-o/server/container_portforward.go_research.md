<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward.go -->
# sources/cloud-native/cri-o/server/container_portforward.go

## Purpose

This file implements CRI port-forward endpoint creation and the streaming callback that forwards traffic into a pod sandbox network namespace.

## Important APIs, Types, and Functions

`Server.PortForward` prepares a streaming URL with `getPortForward`. `StreamService.PortForward` resolves the sandbox, validates readiness and network namespace path, drains the stream asynchronously on return, and delegates to `Runtime().PortForwardContainer`.

## Control Flow

The unary call only prepares the streaming endpoint and wraps setup failures in a generic error. The stream callback defers stream draining to avoid close/memory issues, resolves the full sandbox ID through `PodIDIndex`, loads the sandbox, verifies it is ready, checks `NetNsPath`, and calls the runtime with the sandbox infra container, namespace path, port, and stream.

## State and Persistence Behavior

No durable state is changed. Stream draining creates a goroutine that copies remaining stream data to `io.Discard`.

## Dependencies and Integration Points

It integrates with CRI streaming helpers, pod sandbox indexes, sandbox readiness and network namespace state, the runtime port-forward implementation, and `go.podman.io/storage/pkg/pools.Copy` for drain behavior.

## Risks and Edge Cases

The unary error hides the underlying `getPortForward` reason. Draining in a goroutine depends on stream behavior and could outlive the request. Missing sandbox, unready sandbox, or empty netns path produce direct errors.

## Test Signals

Tests cover successful endpoint preparation, missing sandbox ID setup failure, and stream callback failure when the sandbox is not found. Runtime forwarding and drain behavior are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward.go -->
