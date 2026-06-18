
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers.go

## Purpose

This file contains shared CRI server helpers for path construction, object naming, image/user conversion, target-container validation, runtime option decoding, status resource projection, CRI event creation, sandbox/container status lookup, namespace and SELinux parsing, cgroup path generation, and user namespace comparisons.

## Important APIs, Types, and Functions

Important helpers include `getSandboxRootDir`, `getVolatileSandboxRootDir`, `getSandboxHostname`, `getSandboxHosts`, `getResolvPath`, `getSandboxDevShm`, `makeSandboxName`, `makeContainerName`, `getContainerRootDir`, `getImageVolumeHostPath`, `getVolatileContainerRootDir`, `criContainerStateToString`, `toContainerdImage`, `getUserFromImage`, `validateTargetContainer`, `isInCRIMounts`, `filterLabel`, `getRuntimeOptions`, `unknownContainerStatus`, `copyResourcesToStatus`, `generateAndSendContainerEvent`, `getPodSandboxRuntime`, `getPodSandboxStatus`, `getContainerStatuses`, `hostNetwork`, `getCgroupsPath`, `toLabel`, `checkSelinuxLevel`, `parseUsernsIDMap`, `parseUsernsIDs`, `sameUsernsConfig`, and `sameMapping`.

## Control Flow

Most path helpers are direct joins against configured root or state directories. Image/user helpers parse Docker references, image store references, and image config user strings. `validateTargetContainer` enforces that a PID namespace target exists, belongs to the same sandbox, and is running. `copyResourcesToStatus` builds a CRI `ContainerResources` object from OCI Linux or Windows resource fields, copying CPU, memory, cpuset, hugepage, unified, and Windows affinity values when present.

`generateAndSendContainerEvent` assembles current pod and container statuses, tolerating missing pod status by sending nil, then posts a CRI `ContainerEventResponse`. `hostNetwork` is OS-aware: Windows uses HostProcess, Darwin returns true, and other platforms check Linux namespace mode. User namespace parsing accepts nil config, allows node mode only without mappings, requires pod mode with UID/GID mappings, and rejects unsupported modes.

## State and Persistence Behavior

The helpers mostly compute derived values. They read CRI stores, containerd image references, and runtime options, but do not persist state except for sending event objects to `containerEventsQ`. `copyResourcesToStatus` returns an updated status value for the caller to commit.

## Dependencies and Integration Points

Dependencies include containerd client images and containers, CRI config and stores, runtime API types, OCI specs, typeurl, errdefs, logging, path utilities, and SELinux/user namespace conventions. The functions are used across sandbox creation, container creation/start/status, events, resource update, and image volume workflows.

## Risks and Edge Cases

Name generation uses `_` as a delimiter and depends on metadata uniqueness. `getUserFromImage` discards group information by design. `copyResourcesToStatus` must be kept in sync with new CRI resource fields. `hostNetwork` has platform-specific assumptions. SELinux level validation is regex-based and may reject valid future forms. User namespace comparison treats different mapping order as different and supports only one mapping line.

## Test Signals

Tests cover image user parsing, runtime option generation and typed-nil handling, env deduplication through OCI helpers, robust removal on common paths, PID namespace target validation, Windows affinity projection, and host-network logic. Additional useful tests would cover SELinux levels, cgroup path generation, user namespace parsing, and CRI event contents.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers.go -->
