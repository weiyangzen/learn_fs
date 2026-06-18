# sources/cloud-native/containerd/internal/cri/server/container_create.go

## Purpose

This is the main CRI `CreateContainer` implementation. It validates sandbox/container inputs, reserves unique names, handles checkpoint restore detection, resolves images, builds platform-specific OCI specs, prepares snapshots/volumes/I/O, creates containerd containers, creates CRI store objects, sends events, and invokes NRI hooks.

## Important APIs, Types, and Functions

`CreateContainer` is the public CRI method. `createContainerRequest` carries all inputs for normal and restore create paths. `createContainer` performs the transactional create. `volumeMounts` builds image-defined volume mounts. `runtimeSpec` generates or loads an OCI spec. `platformSpecOpts`, `buildContainerSpec`, `buildLinuxSpec`, `buildWindowsSpec`, and `buildDarwinSpec` compose spec options. `linuxContainerMounts` adds sandbox system file mounts. `runtimeInfo` retrieves runtime metadata from sandbox store or legacy container info.

## Control Flow

`CreateContainer` fetches sandbox and sandbox status, validates metadata and stop signal, reserves the generated CRI name, initializes metadata, detects checkpoint archive/image inputs, and either delegates to `CRImportCheckpoint` or resolves the image and calls `createContainer`.

`createContainer` creates persistent and volatile root directories with rollback cleanup, queries platform/runtime, mutates mounts, builds image volume mounts, gets runtime handler, builds spec, manages SELinux labels, gathers snapshotter opts, creates `ContainerIO` using streaming or FIFO mode, builds platform-specific post-rootfs spec opts, labels and runtime info, appends containerd options including snapshot, volumes, spec, runtime, labels, metadata extension, sandbox association, and NRI adjustment, blocks NRI plugin sync, creates the containerd container, wraps it in the CRI container store with status/resources, adds it to the store, emits a created event, and sends NRI post-create notification.

Spec builders compose OS-specific options for Linux security, namespaces, cgroups, blockio/RDT, annotations, userns, mounts, devices, and resources; Windows process/network/HostProcess/resources/devices/credential spec; and Darwin args/env/mounts.

## State and Persistence Behavior

The create transaction persists container root directories, volatile IO directories, snapshots/rootfs, image volume host directories, containerd container metadata/extensions, CRI container store checkpoints/status, name reservations, SELinux labels, and created events. Deferred cleanup releases names, removes directories, closes IO, deletes containerd containers/snapshots, deletes CRI checkpoint data, and undoes NRI create on errors.

## Dependencies and Integration Points

It integrates CRI sandbox/container stores, sandbox service, image service/resolution, runtime handler config, snapshotters, CRI IO, labels, annotations, OCI opts, blockio/RDT, NRI, tracing, containerd client, and typeurl metadata. It is the central caller of the `opts` package files in this work item.

## Risks and Edge Cases

Rollback ordering is critical to avoid leaked names, snapshots, IO, labels, and store entries. Checkpoint images take a separate path before normal image resolution. User namespace configuration must match sandbox settings. Privileged containers are rejected unless sandbox is privileged. Runtime-handler features gate recursive read-only mounts. Missing log paths disable logging. NRI adjustment can mutate specs or abort creation.

## Test Signals

Tests should cover name reservation conflicts/cleanup, missing metadata, checkpoint path selection, snapshot retry, volume mount generation, platform spec composition, Linux security/userns/namespace errors, Windows HostProcess mismatch, IO type selection, NRI rollback, store add failures, and event emission.
