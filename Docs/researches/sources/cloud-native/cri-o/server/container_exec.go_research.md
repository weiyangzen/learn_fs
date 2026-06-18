<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec.go -->
# sources/cloud-native/cri-o/server/container_exec.go

## Purpose

This file implements asynchronous CRI `Exec` endpoint preparation and the streaming service callback that performs the actual exec.

## Important APIs, Types, and Functions

`Server.Exec` returns a streaming URL for a command in a container. `StreamService.Exec` is called by the streaming layer and invokes the runtime `ExecContainer`.

## Control Flow

`Server.Exec` resolves the container from a short ID and checks the sandbox runtime handler. If the runtime handler is configured for websocket streaming, it asks the runtime to serve exec directly and returns that URL. Otherwise it delegates to `s.getExec(req)` to create the CRI streaming endpoint. The stream callback resolves the container, verifies it is living, and calls `Runtime().ExecContainer` with stdin/stdout/stderr, tty, and resize channel.

## State and Persistence Behavior

The file does not persist state. It creates transient streaming URLs and runtime exec processes. The runtime manages exec lifecycle.

## Dependencies and Integration Points

It integrates with the server container index, sandbox runtime handler lookup, CRI streaming server helpers, runtime websocket capability, runtime monitor exec serving, gRPC status codes, and kube `remotecommand.TerminalSize`.

## Risks and Edge Cases

`Server.Exec` assumes `s.getSandbox(ctx, c.Sandbox())` returns a sandbox; a nil sandbox would panic when reading `RuntimeHandler`. The stream path maps missing or non-living containers to `codes.NotFound`. The websocket path bypasses the standard streaming endpoint setup, so runtime handler configuration must be correct.

## Test Signals

The tests cover successful endpoint creation, invalid requests, missing containers in the stream callback, living-state checks, stopped containers, and allowing exec setup during graceful termination before the kill loop begins.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec.go -->
