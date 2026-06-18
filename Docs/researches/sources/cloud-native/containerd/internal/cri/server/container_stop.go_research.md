# sources/cloud-native/containerd/internal/cri/server/container_stop.go

## Purpose
This file implements CRI `StopContainer`, including idempotence, graceful stop signal selection, timeout fallback to SIGKILL, unknown-state cleanup, shim connection retry, NRI stop notification, and wait helpers.

## Important APIs, Types, and Functions
Key functions are `StopContainer`, `stopContainerRetryOnConnectionClosed`, `stopContainer`, `waitContainerStop`, and `cleanupUnknownContainer`. It uses containerd task APIs, container status channels, CRI stop-signal helpers, image stop signal fallback, NRI, event monitor handling, and tracing/timers.

## Control Flow, State, and Persistence
The RPC returns success for missing containers. Running/unknown containers are stopped; other states return success without action. Unknown tasks get an exit monitor so cleanup can reuse normal exit handling. With positive timeout, a CRI-configured signal, stored metadata signal, image stop signal, or SIGTERM is sent once using an atomic guard; if the container does not stop before the deadline, SIGKILL is sent and the method waits for `container.Stopped()`. Unknown cleanup synthesizes a `TaskExit` event with unknown exit code.

## Dependencies and Integration Points
It integrates with container store status, image service, containerd task wait/kill, shim ttrpc retry detection, NRI sync blocking, lifecycle event handling, CRI stop signal conversion, and metrics.

## Risks and Test Signals
Risks include double-sending graceful signals, leaving unknown containers uncleaned, mishandling deleted images, context timeout races, and shim closed retry behavior. `container_stop_test.go` covers wait behavior and signal conversion helpers.
