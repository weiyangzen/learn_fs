# Research: sources/cloud-native/containerd/client/sandbox.go

## Purpose
Adds a high-level client API for sandbox metadata and sandbox controller lifecycle, including creating containers associated with a sandbox.

## Important APIs, Control Flow, And State
`Sandbox` exposes ID, metadata, labels, container creation, start, stop, wait, and shutdown. `sandboxClient` stores the owning `Client` and `api.Sandbox` metadata. `Client.NewSandbox` validates ID, resolves the default sandboxer, initializes timestamps, applies `NewSandboxOpts`, writes metadata to `SandboxStore`, then calls the sandbox controller `Create`. `Shutdown` first asks the controller to shut down and then deletes metadata, ignoring not-found errors. Options set runtime/typeurl options, apply and marshal OCI specs, attach extensions, and set labels. State spans the sandbox store and sandbox controller implementation.

## Dependencies And Integration
Depends on `core/sandbox`, containers metadata, OCI spec helpers, typeurl, protobuf empty types, and errdefs. It integrates with `Client.NewContainer` through `WithSandbox`.

## Risks And Test Signals
Risks include metadata created before controller create failure, stale metadata on partial failures, option marshaling failures, and shutdown idempotency. Tests should cover empty IDs, default sandboxer resolution, spec option application, runtime/extension encoding, container creation with sandbox label, wait errors, and not-found shutdown handling.
