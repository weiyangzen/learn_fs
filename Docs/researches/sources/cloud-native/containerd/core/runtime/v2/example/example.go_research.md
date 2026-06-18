# sources/cloud-native/containerd/core/runtime/v2/example/example.go

## Purpose
Demonstrates the shape of a runtime v2 shim implementation: plugin registration, shim manager identity, runtime info, task service registration, and the task RPC method set.

## APIs, Flow, State, Dependencies, Risks, And Tests
The package registers a ttrpc task plugin requiring event publisher and shutdown services. `NewManager` returns a `shim.Shim` manager with `Name`, `Start`, `Stop`, and `Info`; only `Info` is implemented, returning runtime name/version. `newTaskService` returns `exampleTaskService`, which implements `shim.TTRPCService` and the generated v2 task service. `RegisterTTRPC` installs the task service. Most task methods return `errdefs.ErrNotImplemented`; `Shutdown` calls `os.Exit(0)`.

There is no durable task state, process tracking, or filesystem persistence. Control flow demonstrates plugin initialization and ttrpc registration rather than real container lifecycle.

Dependencies include bootstrap v1, task v2 API, type protobufs, shim package, shutdown service, plugin registry, ttrpc, and errdefs. It integrates with `example/cmd/main.go`.

Risks are mostly educational: using this as production code would fail all lifecycle operations, and `Shutdown` exits the process immediately. Test signals are compile-time interface conformance and smoke tests that plugin registration and `-info` behavior work.
