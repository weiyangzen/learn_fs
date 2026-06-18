<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_list_test.go -->
# sources/cloud-native/cri-o/server/container_list_test.go

## Purpose

This suite verifies `ListContainers` state mapping and filter behavior.

## Important APIs, Types, and Functions

It uses `sut.ListContainers`, `testContainer.SetCreated`, `testContainer.SetState`, and CRI `ContainerFilter`.

## Control Flow

A table covers created, running, and stopped internal OCI states and whether the container has been marked created. Filter cases cover nonmatching and matching container IDs, sandbox ID combinations, sandbox-only filtering, state filtering, and label selector filtering.

## State and Persistence Behavior

All state is in-memory through the test harness. No persistent storage is touched.

## Dependencies and Integration Points

The suite depends on runtime-spec state constants, CRI container states, and the shared sandbox/container setup helpers.

## Risks and Edge Cases

It does not test streaming list chunking or multi-container ordering. Label filtering is only tested as a nonmatch, not a positive selector match.

## Test Signals

The tests lock down the important invariant that containers not marked created are suppressed from CRI list output.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_list_test.go -->
