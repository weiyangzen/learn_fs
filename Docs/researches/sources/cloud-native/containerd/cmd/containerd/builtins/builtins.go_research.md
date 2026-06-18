# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins.go

## Purpose
Registers the core cross-platform built-in containerd plugins by blank import.

## Important APIs, Control Flow, And State
The import list registers runtime v2, content, events, GC, image verifier, leases, metadata, mount, NRI, restart, sandbox, debug/grpc/metrics/ttrpc servers, service plugins for containers/content/diff/events/health/images/introspection/leases/mounts/namespaces/opt/sandbox/snapshots/streaming/tasks/transfer/version/warning, and transfer/streaming plugins. There are no functions; package initialization performs registration. State is global plugin registry entries.

## Dependencies And Integration
This package is imported by `cmd/containerd` so the daemon knows which plugins are available without dynamic loading.

## Risks And Test Signals
Risks include missing critical plugin imports, unwanted side effects from init functions, and registry ID conflicts. Tests should load the plugin graph and confirm required services are present.
