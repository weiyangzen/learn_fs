<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats.go -->
# sources/cloud-native/cri-o/server/container_stats.go

## Purpose

This file implements unary CRI stats lookup for a single container.

## Important APIs, Types, and Functions

`ContainerStats(ctx, req)` resolves a container by short ID, resolves its sandbox, and returns `s.StatsForContainer(container, sb)`.

## Control Flow

The method starts a span, looks up the container, errors on missing IDs, loads the sandbox from the container's sandbox ID, returns an explicit error if the sandbox is missing, and wraps the computed stats in `ContainerStatsResponse`.

## State and Persistence Behavior

It reads in-memory container and sandbox state plus whatever live cgroup/runtime data `StatsForContainer` reads. It does not mutate state.

## Dependencies and Integration Points

It integrates with container lookup, sandbox lookup, CRI stats protobufs, and the server stats implementation.

## Risks and Edge Cases

Stats accuracy and nil fields are delegated to `StatsForContainer`. A missing sandbox for an existing container is treated as an error, surfacing inconsistent server state.

## Test Signals

Tests cover invalid container lookup. List-stats tests cover stopped-container filtering separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats.go -->
