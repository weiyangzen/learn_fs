# Research: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_freebsd.go

## Purpose
Raises process file descriptor limits for the stress tool on FreeBSD.

## Important APIs, Control Flow, And State
`setRlimit` reads `RLIMIT_NOFILE`, sets current limit to max, and writes it back with `syscall.Setrlimit`. The effect is process-level resource limit mutation before stress workers run.

## Dependencies And Integration
Uses FreeBSD syscall rlimit APIs and is selected by build tags. Called from `main.go` init.

## Risks And Test Signals
Risks include permission failures, platform-specific max semantics, and panics from init if raising limits fails. Platform tests should cover successful no-op/high-limit cases and error propagation.
