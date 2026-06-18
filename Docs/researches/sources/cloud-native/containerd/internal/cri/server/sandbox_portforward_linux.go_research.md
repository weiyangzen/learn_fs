# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_linux.go

## Purpose

This Linux file performs the actual port-forward data path by entering a sandbox network namespace and proxying bytes to localhost inside that namespace.

## Important APIs, Types, and Functions

`portForward` loads the sandbox, chooses either the sandbox netns or host namespace, dials `localhost:<port>` inside the namespace, and copies bytes in both directions between the stream and TCP connection.

## Control Flow

For non-host networking it checks the netns is not closed and uses `NetNS.Do`; host networking runs directly. It dials IPv4 first, then IPv6 to avoid Go Happy Eyeballs running outside the namespace. It waits for one copy direction to finish, then gives the other one second to close or responds to context cancellation.

## State and Persistence Behavior

No persistent state is changed. The stream is closed after namespace execution, and TCP connections are closed with defers.

## Dependencies and Integration Points

It integrates with CNI netns objects, Go networking, CRI streaming server callbacks, and sandbox store network state.

## Risks and Test Signals

Risks include hangs on half-closed streams, failed dual-stack fallback, and closed netns races. Integration tests with real netns and stream cancellation are the main signals.
