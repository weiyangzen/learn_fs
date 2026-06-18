# Research: sources/cloud-native/containerd/client/services.go

## Purpose
Centralizes client service dependencies and provides option helpers for injecting remote or in-memory service implementations.

## Important APIs, Control Flow, And State
The internal `services` struct holds content, images, containers, namespace, snapshotter map, task, diff, events, leases, introspection, sandbox, transfer, and mount services. `ServicesOpt` setters populate those fields; remote gRPC clients are wrapped into store abstractions where needed. `WithSnapshotters` defensively copies the supplied map. `WithInMemoryServices` retrieves required plugin instances from a plugin `InitContext`, maps service plugin names to typed client/store wrappers, and installs the populated `services` struct into client options. State is dependency wiring only; no external persistence occurs here.

## Dependencies And Integration
Uses generated service clients, core service interfaces, plugin registry types, service name constants, and package `maps`. It is the bridge for CRI or other plugins embedding a client without dialing the daemon over gRPC.

## Risks And Test Signals
Risks include panics from wrong plugin instance types, missing service plugin keys, stale service-name mappings, and accidental sharing if future map fields are not copied. Tests should cover each setter, snapshotter map isolation, in-memory service resolution, missing plugin errors, and type assertions.
