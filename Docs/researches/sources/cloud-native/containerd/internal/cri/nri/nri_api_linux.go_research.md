# sources/cloud-native/containerd/internal/cri/nri/nri_api_linux.go

## Purpose

This Linux file implements CRI integration with the Node Resource Interface. It forwards CRI pod/container lifecycle events to NRI, exposes CRI pods and containers as NRI domain objects, allows NRI plugins to adjust OCI specs during container creation, and handles plugin-initiated resource updates or evictions.

## Important APIs, Types, and Functions

`API` holds the CRI implementation and internal NRI API. `NewAPI`, `Register`, `IsDisabled`, and `IsEnabled` manage setup. Lifecycle hooks include `RunPodSandbox`, pod resource update hooks, `StopPodSandbox`, `RemovePodSandbox`, `CreateContainer`, `PostCreateContainer`, start/update/stop/remove container hooks, `NotifyContainerExit`, `UndoCreateContainer`, `WithContainerAdjustment`, `WithContainerExit`, and `BlockPluginSync`.

The NRI domain interface is implemented by `GetName`, list/get pod and container methods, `UpdateContainer`, and `EvictContainer`. Wrappers `criPodSandbox` and `criContainer` expose CRI metadata, labels, annotations, Linux namespaces/resources/devices, CDI devices, seccomp data, PIDs, rlimits, users, and status. `fromCRILinuxResources` and `toCRIResources` convert resource structs.

## Control Flow

Registration registers the CRI domain and starts NRI if enabled. Lifecycle methods short-circuit when disabled, wrap CRI objects, and call matching NRI methods. `RunPodSandbox` compensates failed run by stopping/removing the pod in NRI. `WithContainerAdjustment` unmarshals the OCI spec from a containerd container, asks NRI for adjustments, applies them through an NRI spec generator with resource, RDT, blockio, and CDI resolvers, then re-marshals the adjusted spec. `UpdateContainer` updates CRI status synchronously while calling CRI resource-update logic. `EvictContainer` stops the container through CRI.

## State and Persistence Behavior

The adapter keeps no independent durable state. It reads CRI stores, containerd container metadata, sandbox metadata, OCI specs, and live task PIDs. Spec adjustments mutate the containerd container object before creation persists it. Resource updates mutate CRI container status through `Status.UpdateSync`.

## Dependencies and Integration Points

It depends on containerd client/container metadata, CRI annotations/constants/stores/util, blockio/CDI helpers, NRI APIs and generator, OCI runtime spec, typeurl, errdefs, and CRI protobufs. Container creation appends `WithContainerAdjustment`, defers `UndoCreateContainer`, and blocks plugin sync around new-container operations.

## Risks and Edge Cases

Disabled NRI must be a true no-op. Wrappers tolerate missing store metadata, missing tasks, and deleted network namespaces. Spec adjustment errors abort container creation. Resource conversion omits unsupported fields such as swap and sets OOM score only through the provided argument. `GetPodSandboxID` and `GetName` rely on spec annotations, so missing annotations produce empty identity fields for containerd-only objects.

## Test Signals

Tests should cover disabled behavior, lifecycle forwarding, create adjustment spec mutation, adjustment error rollback, stale netns filtering, resource conversion, plugin update/evict behavior, and wrappers for both CRI-store and raw containerd container inputs.
