<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_status_test.go -->
# sources/cloud-native/cri-o/server/container_status_test.go

## Purpose

This suite validates `ContainerStatus` state mapping and verbose info behavior.

## Important APIs, Types, and Functions

It calls `sut.ContainerStatus`, sets `testContainer` volumes, state, spoofed PID, and spec, and mocks `GetContainerMetadata`.

## Control Flow

A table covers created, running, stopped with exit code zero, stopped with exit code -1, OOM killed, seccomp killed, and running with checkpointing enabled. It expects matching CRI states and verbose JSON content. Additional tests cover invalid container IDs and metadata retrieval errors.

## State and Persistence Behavior

State is in-memory and mock storage metadata is returned through gomock. No real storage metadata is read.

## Dependencies and Integration Points

The suite depends on runtime-spec states, CRI status types, internal storage metadata, and the shared server harness.

## Risks and Edge Cases

It does not assert exact reason/message values for all stopped cases and does not cover runtime status refresh when exit code is initially nil.

## Test Signals

The suite strongly confirms that verbose status includes runtime spec JSON and checkpoint fields only when checkpoint restore support is enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_status_test.go -->
