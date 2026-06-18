<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats_list.go -->
# sources/cloud-native/cri-o/server/container_stats_list.go

## Purpose

This file implements CRI list and stream APIs for container stats.

## Important APIs, Types, and Functions

`ListContainerStats`, `StreamContainerStats`, and `listContainerStats` expose stats for non-stopped containers. `listContainerStats` reuses container filtering logic by converting a stats filter into a `types.ContainerFilter`.

## Control Flow

The list function gets internal containers whose state is not stopped. If a filter is present, it filters by ID, pod sandbox ID, and labels using `filterContainerList` and `filterContainer`. It then calls `s.StatsForContainers`. The stream variant chunks responses by `streamChunkSize`.

## State and Persistence Behavior

The file reads in-memory container state and live stats data but does not persist or mutate state.

## Dependencies and Integration Points

It integrates with `ContainerServer.ListContainers`, internal OCI container states, CRI stats filters, shared list filtering helpers, and stats aggregation helpers.

## Risks and Edge Cases

Stopped containers are excluded before filters, so a direct stats filter for a stopped container yields empty. Filters share semantics with `ListContainers`, including empty results for unresolved IDs. Streaming errors abort the stream.

## Test Signals

Tests cover empty stats for no running containers, stopped container filtering, and invalid ID filters returning empty.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats_list.go -->
