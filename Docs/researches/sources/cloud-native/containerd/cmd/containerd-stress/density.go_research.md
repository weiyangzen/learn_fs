# Research: sources/cloud-native/containerd/cmd/containerd-stress/density.go

## Purpose
Adds the `density` subcommand, which creates many containers and reports process memory map/stat information for density analysis.

## Important APIs, Control Flow, And State
`densityCommand` validates count, creates a client in the `density` namespace, cleans previous containers, pulls/unpacks the image, then loops creating containers/tasks with sleep specs while collecting PIDs until count or signal interruption. It writes JSON results when requested and includes helpers `getMaps`, `getppid`, `parseStat`, and `Stat` for reading `/proc/<pid>/maps` and `/proc/<pid>/stat` style data. Persistent state is temporary containers/tasks/snapshots in the density namespace and host procfs reads.

## Dependencies And Integration
Uses the client package, `cio`, OCI spec helpers, namespaces, CLI flags inherited from the main app, JSON, procfs file reads, and signal handling.

## Risks And Test Signals
Risks include Linux `/proc` assumptions, cleanup after signal interruption, stat parsing edge cases with process names, and resource exhaustion at high counts. Tests should cover count validation, stat parsing, map aggregation, cleanup behavior, and JSON output shape.
