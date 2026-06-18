# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/plugin/plugin_linux.go

## Purpose
Registers the runc v2 shim task service plugin for Linux builds.

## Important APIs, Control Flow, And State
`init` registers a plugin with the containerd plugin registry under the shim task service type and runc v2 service ID. The init function constructs the service by calling `task.NewTaskService` with shim publisher and shutdown service dependencies. Persistent state is plugin registry registration; runtime service state is created later per shim.

## Dependencies And Integration
Uses the task package, shim/shutdown services, containerd plugin registry, and plugin ID constants. The blank import in `main.go` relies on this side effect so the shim exposes the ttrpc task API.

## Risks And Test Signals
Risks include registration ID/type drift, missing required dependencies, and Linux-only build coverage. Tests should confirm plugin registration, service construction from an init context, and shim startup exposing task v3.
