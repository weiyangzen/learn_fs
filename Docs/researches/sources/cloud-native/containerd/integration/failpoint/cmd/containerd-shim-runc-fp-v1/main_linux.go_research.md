# sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/main_linux.go

## Purpose

This small Linux binary starts a failpoint-enabled runc shim manager under runtime type `io.containerd.runc-fp.v1`. It is the executable entry point for tests that need a shim with injected ttrpc task API failures.

## Important APIs, Types, And Functions

- `main` calls `shim.RunShim(context.Background(), manager.NewShimManager("io.containerd.runc-fp.v1"))`.
- The behavior is extended by the package-level plugin registration in `plugin_linux.go`.

## Control Flow

Startup is delegated entirely to containerd's shim runner and runc v2 manager. The custom runtime type name distinguishes this shim from the normal runc runtime so integration test configs can opt into failpoint behavior.

## State And Persistence Behavior

This file does not persist state itself. Runtime state is managed by the shim manager and plugins loaded in the same package.

## Dependencies And Integration Points

It integrates with containerd's `cmd/containerd-shim-runc-v2/manager` and `pkg/shim` packages. The companion plugin registers the task service implementation that injects failpoints.

## Risks And Edge Cases

The runtime type name must match test containerd configuration. If the companion plugin fails to initialize, the shim starts without the expected task failpoint behavior or fails during plugin setup.

## Test Signals

Indirect tests using `failpointRuntimeHandler` validate that this entry point can run a shim and expose the failpoint task service.
