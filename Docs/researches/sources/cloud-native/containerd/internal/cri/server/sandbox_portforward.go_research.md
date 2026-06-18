# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward.go

## Purpose

This file implements the CRI `PortForward` RPC entrypoint that returns a streaming endpoint for a ready pod sandbox.

## Important APIs, Types, and Functions

`PortForward` looks up the sandbox by requested ID, verifies it is ready, and delegates endpoint creation to `streamServer.GetPortForward`.

## Control Flow

The method fails if the sandbox cannot be found or is not ready. It does not validate requested ports against pod declarations.

## State and Persistence Behavior

No state is mutated. It reads the sandbox store and allocates a streaming server response.

## Dependencies and Integration Points

It integrates with CRI streaming server setup and platform-specific `portForward` implementations that execute the actual byte forwarding.

## Risks and Test Signals

Risks include allowing undeclared ports and stale ready state. Streaming integration tests are needed for full coverage.
