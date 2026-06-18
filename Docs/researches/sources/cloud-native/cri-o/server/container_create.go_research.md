<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create.go -->
# sources/cloud-native/cri-o/server/container_create.go

## Purpose

This file is the main CRI `CreateContainer` implementation and the shared container construction pipeline for CRI-O. It translates a Kubernetes CRI container request into storage state, an OCI runtime spec, an `oci.Container` object, runtime registration, persisted state, CRI events, and cleanup behavior.

## Important APIs, Types, and Functions

`CreateContainer` validates the CRI request, resolves the sandbox, detects checkpoint images, reserves names, creates the storage and runtime container, persists state, and emits the create event. `createSandboxContainer` builds almost all OCI spec details. Helper types `orderedMounts`, `criOrderedMounts`, and `containerImageResult` support mount ordering and image resolution. Important helpers include `setupContainerUser`, `addImageVolumes`, `setupContainerMounts`, `setupContainerEnvironmentAndWorkdir`, `setupSeccomp`, `setupBaseContainerMounts`, `configureSELinuxLabels`, `createStorageContainer`, `resolveAndVerifyContainerImage`, `setupContainerIDMappings`, `setupContainerEtcDirectory`, `setupContainerRuntimeAndStopSignal`, `setupLinuxResources`, and `setupCgroupNamespace`.

## Control Flow

Creation first rejects missing config, image, sandbox config, or sandbox metadata. With checkpoint-restore enabled, a local archive or OCI image annotated as a checkpoint diverts to `CRImportCheckpoint`. Normal creation retrieves the pod sandbox under the sandbox stop mutex, creates a factory container, assigns CRI config, reserves the container name, and stages cleanup handlers. `createSandboxContainer` filters annotations, sets privilege and security context defaults, resolves/verifies the image, creates the storage container, configures SELinux, bind/image/artifact mounts, devices, storage mount, resources, namespaces, sysfs and shm mounts, process args, seccomp, runtime path, annotations, workload mutations, environment, workdir, hooks, CDI devices, pids limit, ID mappings, `/etc`, rootless changes, NRI create hooks, optional log links, and writes `config.json` into both persistent and run directories. The outer function then adds indexes, calls platform runtime creation, writes state, handles context cancellation specially, marks created, sends NRI post-create and CRI created events, and returns the ID.

## State and Persistence Behavior

State is spread across name reservations, resource-store stages, storage containers, runtime containers, in-memory server maps, truncation ID indexes, `config.json` files in storage/run dirs, container state on disk, seccomp notifier storage, and CRI event channels. `resourcestore.ResourceCleaner` rolls back staged resources unless creation succeeds or a context error requires the partially created resource to be stored for retry/wait behavior. Storage creation and storage start have deferred cleanup. `ContainerStateToDisk` is best-effort on successful creation and on context-cancel handoff.

## Dependencies and Integration Points

The code integrates with CRI protobuf types, internal factory `container`, `sandbox`, `oci`, runtime and storage servers, SELinux/security labeling helpers, OpenContainers runtime-tools `generate`, containers/storage, image signature policy, NRI, runtime-handler hooks, CDI injection, subscriptions/default mounts, timezone setup, kubelet labels, resource-store, annotations v2, AppArmor/seccomp/blockio/RDT helpers, and checkpoint restore.

## Risks and Edge Cases

This is a high-blast-radius path. Risks include cleanup ordering bugs, context timeout handoff leaving inconsistent state, mount path traversal or symlink handling mistakes, SELinux relabel decisions for privileged and host namespace combinations, generated `/etc/passwd` or `/etc/group` shadowed by CRI mounts, untrusted image annotations, namespace target lookup failures, missing image config, user namespace ownership/accessibility errors, malformed umask annotations, and signature-policy behavior differing by namespace. The code carefully uses `securejoin`, rejects some absent mount sources, sorts mounts to avoid shadowing, and treats duplicate create requests by checking reserved names and resource-store waits.

## Test Signals

The paired tests cover invalid create requests, stopped/missing sandboxes, checkpoint archive errors, Linux bind mount behavior, recursive read-only constraints, cgroup mount read/write mode, idmapped mount support, and path-subdirectory checks. Broader integration coverage is still important for successful end-to-end creation, NRI/hook failures, seccomp notifier registration, context cancellation retry paths, SELinux relabeling, and user namespace combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create.go -->
