# sources/cloud-native/containerd/core/runtime/v2/example/cmd/main.go

## Purpose
Entrypoint for the example runtime v2 shim binary. It wires the example shim manager into the generic shim runner.

## APIs, Flow, State, Dependencies, Risks, And Tests
`main` calls `shim.RunShim(context.Background(), example.NewManager("io.containerd.example.v1"))`. There are no flags, persistent state, or local error handling in this file.

It depends on the local `example` package and containerd's `pkg/shim` runner. Integration is instructional: a real shim binary can follow this shape to register services and run under containerd's shim bootstrap protocol.

Risks are that this is intentionally skeletal; operational behavior lives in the runner and example manager. Test signals are compile checks and running the example shim enough to confirm it registers and exits through the shim framework.
