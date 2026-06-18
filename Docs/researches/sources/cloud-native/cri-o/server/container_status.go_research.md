<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_status.go -->
# sources/cloud-native/cri-o/server/container_status.go

## Purpose

This file implements CRI `ContainerStatus`, including status fields, mounts, resources, exit reasons, log path, and verbose info JSON.

## Important APIs, Types, and Functions

`ContainerStatus(ctx, req)` builds `types.ContainerStatusResponse`. Constants define CRI reasons: `OOMKilled`, `seccomp killed`, `Completed`, and `Error`. `containerInfo` and `containerInfoCheckpointRestore` are verbose JSON payload shapes. `createContainerInfo` loads storage metadata and marshals runtime spec, sandbox ID, pid, privileged flag, and optional checkpoint fields.

## Control Flow

The method resolves the container, fills ID, metadata, labels, annotations, image ID/ref/name, and runtime user. It converts tracked volumes into CRI mounts. If the spec has Linux resources, it includes stored resources. For stopped containers lacking an exit code, it asks the runtime to update status and rereads state. It maps internal created/running/paused/stopped states to CRI states and sets start/finish timestamps, exit code, reason, and message. Verbose requests call `createContainerInfo` and attach the JSON string under `info`.

## State and Persistence Behavior

The main path reads container state. The fallback `UpdateContainerStatus` can mutate in-memory state by refreshing exit code and runtime status. Verbose info reads storage metadata. No disk writes occur here.

## Dependencies and Integration Points

It integrates with container lookup, internal OCI state, storage runtime metadata, goccy JSON, OpenContainers runtime spec, checkpoint restore configuration, and CRI status protobufs.

## Risks and Edge Cases

`StateNoLock` is used initially, so concurrent state changes can affect consistency until state is refreshed. Unknown states remain `CONTAINER_UNKNOWN`. Exit code nil after refresh maps to `-1`. Verbose info fails the whole request if storage metadata retrieval or JSON marshal fails.

## Test Signals

Tests cover created/running/stopped/OOM/seccomp state mapping, mount reporting, verbose JSON with runtime spec, checkpoint fields when enabled, invalid IDs, and storage metadata errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_status.go -->
