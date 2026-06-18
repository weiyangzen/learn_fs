<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats_test.go -->
# sources/cloud-native/cri-o/server/container_stats_test.go

## Purpose

This suite tests single-container stats failure and list-stats filtering behavior.

## Important APIs, Types, and Functions

It calls `sut.ContainerStats` and `sut.ListContainerStats`, mutates `testContainer` state, and uses CRI stats requests.

## Control Flow

The single stats test sends an empty request and expects an error. List stats tests create a container and expect empty stats when it is not running, explicitly mark it stopped and expect empty stats, and pass an invalid ID filter and expect an empty successful response.

## State and Persistence Behavior

The tests use only in-memory state.

## Dependencies and Integration Points

They depend on the shared server test harness and internal `oci.ContainerState`.

## Risks and Edge Cases

They do not verify actual CPU, memory, writable layer, or timestamp fields. Streaming stats is not covered.

## Test Signals

The tests confirm list stats is non-erroring for filters with no matches and excludes stopped containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats_test.go -->
