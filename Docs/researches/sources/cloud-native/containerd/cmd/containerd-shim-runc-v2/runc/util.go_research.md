# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/util.go

## Purpose
Provides utility logic for deciding whether the shim should kill all remaining processes when the container init exits.

## Important APIs, Control Flow, And State
`ShouldKillAllOnExit` reads the bundle's OCI `config.json`; on read errors it logs and returns true. If the spec has a Linux private PID namespace (`type=pid` with empty path), it returns false because child processes should be reaped with the namespace. Otherwise it returns true to kill remaining processes, especially for shared PID namespace cases. `readSpec` opens and JSON-decodes `config.json`. State is read-only bundle filesystem access.

## Dependencies And Integration
Uses OCI runtime spec, logging, and JSON/filepath helpers. It is called by `task.service.handleInitExit` before waiting for exec exits and publishing init exit.

## Risks And Test Signals
Risks include conservative kill-all on malformed specs, namespace interpretation errors, and bundle path assumptions. Tests should cover missing/malformed config, private PID namespace, shared PID namespace, non-Linux specs, and logging/error behavior.
