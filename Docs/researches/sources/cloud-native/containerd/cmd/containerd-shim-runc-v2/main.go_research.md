# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/main.go

## Purpose
Entrypoint for the Linux runc v2 shim binary.

## Important APIs, Control Flow, And State
`main` calls `shim.RunShim(context.Background(), manager.NewShimManager("io.containerd.runc.v2"))`. The blank import of the task plugin registers the shim task service. Runtime state is managed by the shim framework and manager/service implementations, not this file.

## Dependencies And Integration
Depends on the shim package, runc shim manager, and task plugin registration. It is invoked both as a bootstrap manager binary and as the long-lived shim process spawned by `manager.Start`.

## Risks And Test Signals
Risks are registration/name mismatches and build-tag/platform assumptions. Smoke tests should start the shim through containerd, confirm the runtime name is recognized, and verify the task service is registered.
