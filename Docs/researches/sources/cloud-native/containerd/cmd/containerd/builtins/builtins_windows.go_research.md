# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_windows.go

## Purpose
Registers Windows-specific daemon diff and snapshotter plugins.

## Important APIs, Control Flow, And State
Blank imports register LCOW and Windows diff plugins plus LCOW and Windows snapshotters. There are no functions or direct local state; plugin registration happens through package init side effects.

## Dependencies And Integration
Selected for Windows builds and included through the daemon builtins package.

## Risks And Test Signals
Risks include missing Windows/LCOW plugin registration or build breakage from platform APIs. Windows build and plugin graph tests should verify expected plugins are registered.
