# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_freebsd.go

## Purpose
Registers FreeBSD-specific daemon builtins.

## Important APIs, Control Flow, And State
Blank imports register the walking diff plugin and ZFS plugin for FreeBSD builds. No direct functions or local state are defined; registration happens in imported package initializers.

## Dependencies And Integration
Selected by FreeBSD build constraints and included through the daemon's `builtins` package.

## Risks And Test Signals
Risks include missing snapshot/diff support on FreeBSD if imports drift or dependencies fail. Build and plugin graph tests on FreeBSD should verify registrations.
