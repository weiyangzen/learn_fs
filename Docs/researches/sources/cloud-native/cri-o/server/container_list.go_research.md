<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_list.go -->
# sources/cloud-native/cri-o/server/container_list.go

## Purpose

This file implements CRI container listing and streaming with ID, sandbox, state, and label filters.

## Important APIs, Types, and Functions

`filterContainer` applies state and label selectors to CRI `Container` objects. `filterContainerList` narrows internal `oci.Container` lists by container ID and pod sandbox ID. `ListContainers`, `StreamContainers`, and `listContainers` expose unary and chunked-stream CRI APIs.

## Control Flow

`listContainers` retrieves internal containers, applies ID or sandbox prefiltering if requested, skips containers that are not marked created, converts each to a CRI container, and applies state/label filtering. `filterContainerList` treats nonmatching filtered IDs as an empty result, not an error. `StreamContainers` sends results in `streamChunkSize` batches.

## State and Persistence Behavior

The code reads in-memory container and sandbox indexes only. It does not update state. The `Created()` gate prevents half-created containers from being listed.

## Dependencies and Integration Points

It depends on Kubernetes field selectors, CRI protobuf filters, CRI-O internal container lists, sandbox lookup, and shared stream chunking constants.

## Risks and Edge Cases

Short-ID filtering depends on prefix resolution. A sandbox filter that cannot be resolved silently returns empty. Label filtering uses exact field selector matching. The function logs but does not return errors for nonmatching container IDs, matching CRI list semantics.

## Test Signals

The list tests verify created/running/stopped state mapping, skip of not-created containers, ID and sandbox filtering, and state/label filters returning empty when not matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_list.go -->
