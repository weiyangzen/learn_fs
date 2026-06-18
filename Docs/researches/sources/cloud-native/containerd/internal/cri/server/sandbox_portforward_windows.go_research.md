# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_windows.go

## Purpose

This Windows file implements port forwarding by dialing the pod IP or localhost and proxying bytes between the CRI stream and TCP connection.

## Important APIs, Types, and Functions

`portForward` loads the sandbox, resolves the pod IP with `getIPs` for non-host networking or uses `localhost` for HostProcess/host networking, dials the requested port, and starts bidirectional `io.Copy` goroutines.

## Control Flow

The function waits for the first copy direction or context cancellation, then waits up to one second for the second direction. Errors are wrapped with pod ID and pod IP context.

## State and Persistence Behavior

No persistent state is changed. Network connections are closed by defers.

## Dependencies and Integration Points

It integrates with Windows CRI networking state, sandbox store IP lookup helpers, streaming server callbacks, and Go TCP networking.

## Risks and Test Signals

Risks include stale pod IPs and stream half-close timing. Windows networking integration tests are needed beyond compile coverage.
