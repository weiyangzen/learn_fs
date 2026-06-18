# Research: sources/cloud-native/containerd/cmd/containerd-stress/main.go

## Purpose
Defines the `containerd-stress` CLI, global metrics, configuration, main run modes, cleanup, and result aggregation for containerd load tests.

## Important APIs, Control Flow, And State
`init` registers metrics, raises rlimits, and customizes CLI help/version flags. `main` builds CLI flags for address, concurrency, duration, CRI, exec, image, metrics, runtime, snapshotter, and JSON, then dispatches to metrics server, CRI test, normal test, or density subcommand. `serve` starts an HTTP metrics endpoint and records binary sizes. `criTest` and `test` set namespaces, create clients, cleanup old resources, pull images for non-CRI, start worker goroutines for the duration, gather counts, log and optionally JSON-encode results. `cleanup` deletes existing stress namespace containers/tasks/snapshots. State includes remote containerd/CRI resources, metrics registry, HTTP server, and worker counters.

## Dependencies And Integration
Uses containerd client/defaults/plugins/version, CRI remote service, namespaces, Docker metrics, urfave/cli, OS signals, and worker implementations.

## Risks And Test Signals
Risks include cleanup deleting all containers in the stress namespace, no graceful HTTP server shutdown, unsynchronized counters by design, divide-by-zero if no completions, and long-running resource pressure. Tests should cover CLI config mapping, JSON output, cleanup fallback, signal cancellation, metrics handler startup, and result aggregation with zero totals.
