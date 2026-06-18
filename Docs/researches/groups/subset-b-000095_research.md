# subset-b-000095 research

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_freebsd.go -->
# sources/cloud-native/cri-o/server/container_create_freebsd.go

## Purpose

This file supplies FreeBSD-specific implementations for helpers that Linux creation shares through common names. It lets the common `container_create.go` path compile while omitting Linux-only behavior such as AppArmor, sysfs setup, FIPS toggles, systemd mounts, and user-namespace remapping.

## Important APIs, Types, and Functions

`finalizeUserMapping`, `setContainerConfigSecurityContext`, `disableFipsForContainer`, `addSysfsMounts`, `setOCIBindMountsPrivileged`, `addOCIBindMounts`, `addShmMount`, `setupSystemdMounts`, `getSpecGen`, `specSetApparmorProfile`, `specSetBlockioClass`, and `specSetDevices` mirror the Linux helper surface. `addOCIBindMounts` is the substantial function and supports CRI bind mounts with simple read-only/read-write options.

## Control Flow

FreeBSD bind mount setup sorts CRI mounts, removes default OCI mounts shadowed by explicit `/dev` or `/sys` mounts, validates container and host paths, warns on mounting host `/` over container `/`, resolves symlinks, creates missing sources except during restore, rejects configured absent sources, and returns `oci.ContainerVolume` plus OCI mount specs. `getSpecGen` clears rlimits, adds configured ulimits, applies root read-only state, and adds tmpfs mounts for read-only roots where CRI did not override them. Device setup still delegates to configured devices and annotation parsing.

## State and Persistence Behavior

The file mutates the in-memory OCI spec generator by clearing and adding mounts and rlimits. It may create missing host source directories with `os.MkdirAll`. It has no runtime persistence of its own beyond data consumed by the common creation pipeline.

## Dependencies and Integration Points

It depends on CRI types, runtime-tools generate, OpenContainers runtime spec, internal device parsing, sandbox metadata, storage container info, CRI-O annotation helpers, and the common server/runtime objects. It integrates as the FreeBSD counterpart for helper functions called from the shared create path.

## Risks and Edge Cases

Compared to Linux, mount propagation, recursive read-only, ID-mapped mounts, image volume mounts, SELinux, AppArmor, blockio, and systemd behavior are largely absent or no-op. The function still creates missing host paths, which can surprise restore flows if the restore check regresses. The use of `golang.org/x/net/context` instead of the standard package is harmless but atypical.

## Test Signals

There are no FreeBSD-specific tests in this subset. Linux tests exercise the richer shared helper contract but do not validate this simplified platform behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_generic.go -->
# sources/cloud-native/cri-o/server/container_create_generic.go

## Purpose

This build-tagged file provides `createContainerPlatform` for `windows`, `darwin`, and `freebsd`, delegating directly to the configured runtime without Linux-specific bundle ownership preparation.

## Important APIs, Types, and Functions

The only function is `createContainerPlatform(ctx, container, cgroupParent, idMappings) error`. It accepts the same parameters as the Linux implementation but ignores ID mappings and simply calls `s.ContainerServer.Runtime().CreateContainer(ctx, container, cgroupParent, false)`.

## Control Flow

There is no local branching. The common `CreateContainer` path calls this after storage and in-memory container state are prepared; this platform implementation forwards the call to the runtime.

## State and Persistence Behavior

This file does not persist anything directly. Runtime-side state is created by the runtime implementation. Unlike Linux, it does not call `makeAccessible` on bundle or mount paths for user namespace root mappings.

## Dependencies and Integration Points

It integrates with the shared creation pipeline through the same method signature and depends on internal `oci.Container`, containers/storage `idtools` for API compatibility, and the CRI-O runtime abstraction.

## Risks and Edge Cases

The broad build tag includes FreeBSD even though `container_create_freebsd.go` supplies many other FreeBSD helpers. Any platform needing pre-runtime filesystem preparation must implement it here or split the build tags.

## Test Signals

No direct tests are present. Coverage comes only through platform builds and runtime integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_generic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux.go -->
# sources/cloud-native/cri-o/server/container_create_linux.go

## Purpose

This file implements Linux-specific container creation helpers for runtime creation, user namespace mapping, bind mounts, image and artifact volume mounts, cgroup/sysfs/systemd mounts, AppArmor, blockio, devices, and base spec generation.

## Important APIs, Types, and Functions

`createContainerPlatform` creates the runtime container and makes bundle/mount paths executable for mapped root. `finalizeUserMapping` remaps process user IDs into user namespaces. `setContainerConfigSecurityContext`, `newLinuxContainerSecurityContext`, and `getSpecGen` initialize Linux spec defaults. `addOCIBindMounts` is the main CRI mount translator. `mountArtifact`, `FilterMountPathsBySubPath`, `mountImage`, and `ensureImageVolumesPath` implement image/artifact volume support. `setupSystemdMounts`, `addSysfsMounts`, `addShmMount`, `specSetApparmorProfile`, `specSetBlockioClass`, and `specSetDevices` complete platform-specific spec configuration.

## Control Flow

Mount setup sorts CRI mounts by path depth, removes default mounts shadowed by user `/dev` or `/sys`, reads host mount propagation data, optionally prepares a clean shared `image-volumes` directory, then iterates CRI mounts. Image mounts prefer OCI artifact mounts when enabled and fall back to mounted storage images; host mounts resolve symlinks, reject dangerous absent paths, create missing sources when not restoring, apply propagation rules, enforce recursive read-only constraints, optionally relabel for SELinux, validate ID-mapped mount runtime support, and return OCI mount specs. If `/sys` was not explicitly mounted, it adds a cgroup mount with RO/RW based on cgroup v2 annotation. Systemd setup adds tmpfs mounts, writable cgroup v2 mount or systemd cgroup bind, and `container=crio`.

## State and Persistence Behavior

This file mutates the OCI spec generator and may write files/directories: FIPS disabling writes `sysctl-fips`, missing host paths are created, image volume root is created and checked for emptiness, storage images are mounted, safe subpath mounts are opened, SELinux labels may be applied, and bundle/mount paths may have execute bits widened for mapped root access. Safe mounts are returned for caller cleanup.

## Dependencies and Integration Points

It depends on Linux cgroup detection, runtime feature probes for ID-mapped and recursive read-only mounts, containers/storage mounts, runtime-tools `generate`, OCI artifact store, image status/signature checks, device annotations, AppArmor config, Intel goresctrl blockio, sandbox annotations, CRI mount fields, and the internal container factory/spec APIs.

## Risks and Edge Cases

Risks cluster around mount safety and runtime feature mismatches. Recursive read-only requires runtime support, read-only source, and private propagation. Image volume overlay lowerdir construction depends on a clean shared lower path. Artifact subpaths must exist and are rewritten relative to the requested subpath. `ensureImageVolumesPath` rejects a non-empty directory, so stale files can block creation. `isSubDirectoryOf` intentionally checks whether the storage root is under a requested host path to force host-to-container propagation. SELinux relabels are skipped for SPC types and may be optional via annotation. User namespace remapping is skipped when default ID mappings are configured.

## Test Signals

The Linux tests cover `/dev` and `/sys` default mount filtering, recursive read-only success and error cases, cgroup RW/RO option selection, idmapped mount support errors, and `isSubDirectoryOf`. Remaining high-value coverage includes artifact and image volume mounts, safe subpath cleanup, SELinux relabel modes, systemd mount choices, AppArmor failure paths, and read-only root tmpfs injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux_test.go -->
# sources/cloud-native/cri-o/server/container_create_linux_test.go

## Purpose

This file unit-tests Linux-specific mount helper behavior used during container creation.

## Important APIs, Types, and Functions

Tests directly exercise `addOCIBindMounts` and `isSubDirectoryOf` with factory containers and minimal `storage.ContainerInfo`. Cases include explicit `/dev`, explicit `/sys`, recursive read-only mounts, cgroup mount flags, and ID-mapped mount support.

## Control Flow

Each test constructs a container with targeted CRI mount fields, invokes `addOCIBindMounts`, and inspects returned bind mounts or generated spec mounts. Table-driven recursive read-only tests verify exact error strings for missing runtime support, conflicting read-write mode, and non-private propagation.

## State and Persistence Behavior

The tests mutate in-memory OCI specs only. They intentionally use host paths like `/mnt` or `/sys` without requiring real mount operations, because `addOCIBindMounts` builds specs and only creates missing sources when necessary.

## Dependencies and Integration Points

They depend on `internal/factory/container`, CRI types, and `internal/storage.ContainerInfo`. Because tests are in package `server`, they can call unexported helpers.

## Risks and Edge Cases

The tests verify several mount-safety invariants but do not cover image volume mounting, artifact subpaths, SELinux labels, propagation shared/slave validation, safe mount lifecycle, or systemd-specific behavior. Some tests are sensitive to host path existence and cgroup behavior.

## Test Signals

These tests are strong signals for the path-shadowing and recursive read-only rules. They also lock down the intended behavior that idmapped CRI mounts fail unless the runtime reports support.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_test.go -->
# sources/cloud-native/cri-o/server/container_create_test.go

## Purpose

This Ginkgo suite tests high-level `CreateContainer` validation and early error behavior.

## Important APIs, Types, and Functions

The tests use `sut.CreateContainer`, helper constructors for CRI container and sandbox configs, `addContainerAndSandbox`, and sandbox state mutation.

## Control Flow

Cases call `CreateContainer` with missing image, missing metadata, nil config, stopped sandbox, empty checkpoint archive, missing sandbox, invalid sandbox ID, and empty sandbox ID. They assert that responses are nil and errors occur where expected.

## State and Persistence Behavior

The suite sets up and tears down a mock server environment. The empty checkpoint archive test creates and removes a local `empty.tar`, triggering the checkpoint-detection branch when checkpoint restore is enabled by server configuration.

## Dependencies and Integration Points

It depends on the shared server test harness, CRI protobuf types, and the sandbox/container setup helpers.

## Risks and Edge Cases

This suite does not validate successful creation or deep cleanup behavior. It mostly guards request validation and sandbox lookup semantics, leaving storage/runtime/NRI/hook behavior to other integration tests.

## Test Signals

The tests confirm that bad input is rejected before expensive runtime work and that invalid checkpoint archives surface errors through the create path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_unsupported.go -->
# sources/cloud-native/cri-o/server/container_create_unsupported.go

## Purpose

This build-tagged file handles platforms that are neither Linux nor FreeBSD by making sandbox container creation explicitly unsupported.

## Important APIs, Types, and Functions

`createSandboxContainer(ctx, ctr, sb)` returns `(nil, fmt.Errorf("not implemented yet"))` for `!linux && !freebsd` builds.

## Control Flow

The shared `CreateContainer` path will reach this method after early validation and name reservation. The method immediately fails, causing the outer cleanup chain to run.

## State and Persistence Behavior

No direct state is written here. Any state already staged by the caller should be cleaned by `CreateContainer` resource cleaners.

## Dependencies and Integration Points

It keeps the server package buildable on unsupported platforms by satisfying the method required by the common create path.

## Risks and Edge Cases

The generic error is intentionally blunt and not CRI-typed. If unsupported platforms should expose more precise API behavior, this would need better error mapping.

## Test Signals

No direct tests are included; build-tag compilation is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events.go -->
# sources/cloud-native/cri-o/server/container_events.go

## Purpose

This file implements CRI container event streaming to connected clients.

## Important APIs, Types, and Functions

`containerEventConn` tracks one stream connection with a done channel, `sync.Once`, and stored error. `GetContainerEvents` registers a CRI stream client and waits until it should terminate. `broadcastEvents` fans events from `s.ContainerEventsChan` to all registered clients.

## Control Flow

If pod events are disabled, `GetContainerEvents` returns immediately. Otherwise, `containerEventStreamBroadcaster.Do` starts the single broadcast goroutine. Each client is stored in `containerEventClients`, waits on its connection channel, then is removed. The broadcaster ranges over `ContainerEventsChan`, sends each event to all current streams, records non-transport-close errors, and closes the affected connection. When the event channel closes, all clients are notified.

## State and Persistence Behavior

State is in-memory only: the client map, connection channels, stored send errors, and the event channel. There is no disk persistence. `done` uses `sync.Once` to avoid double-close panics.

## Dependencies and Integration Points

It integrates with CRI `RuntimeService_GetContainerEventsServer`, server config `EnablePodEvents`, `ContainerEventsChan`, and event generation in create/start/remove paths.

## Risks and Edge Cases

The broadcaster sends synchronously to all clients, so a slow or blocked stream can delay delivery to others. Closed transport errors are treated as expected, but other send errors are returned to that connection only after `wait` unblocks. Channel closure is the global shutdown signal.

## Test Signals

The event tests verify single-client delivery and multi-client fanout. They do not cover disabled events, send errors, slow clients, or channel shutdown races beyond the delayed close helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events_test.go -->
# sources/cloud-native/cri-o/server/container_events_test.go

## Purpose

This Ginkgo suite validates container event fanout behavior.

## Important APIs, Types, and Functions

The tests use mock `RuntimeService_GetContainerEventsServer` streams, `sut.ContainerEventsChan`, and `sut.GetContainerEvents`.

## Control Flow

One test sends three events before calling `GetContainerEvents` for a single client and expects each `Send`. Another starts two clients in goroutines, waits for registration, sends the same events, and expects both clients to receive all events. A goroutine closes the event channel after two seconds to unblock stream waits.

## State and Persistence Behavior

All state is in memory. The tests rely on channel buffering/scheduling and mock expectations; no files are written.

## Dependencies and Integration Points

They depend on the server test harness and generated mocks from `test/mocks/containereventserver`.

## Risks and Edge Cases

The tests use sleeps, so timing can be fragile. They do not test send failures, client disconnect handling, disabled events, or cleanup of client map entries.

## Test Signals

The suite confirms that the broadcaster is shared and that events are delivered to all active clients, which is the core contract for CRI event streaming.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec.go -->
# sources/cloud-native/cri-o/server/container_exec.go

## Purpose

This file implements asynchronous CRI `Exec` endpoint preparation and the streaming service callback that performs the actual exec.

## Important APIs, Types, and Functions

`Server.Exec` returns a streaming URL for a command in a container. `StreamService.Exec` is called by the streaming layer and invokes the runtime `ExecContainer`.

## Control Flow

`Server.Exec` resolves the container from a short ID and checks the sandbox runtime handler. If the runtime handler is configured for websocket streaming, it asks the runtime to serve exec directly and returns that URL. Otherwise it delegates to `s.getExec(req)` to create the CRI streaming endpoint. The stream callback resolves the container, verifies it is living, and calls `Runtime().ExecContainer` with stdin/stdout/stderr, tty, and resize channel.

## State and Persistence Behavior

The file does not persist state. It creates transient streaming URLs and runtime exec processes. The runtime manages exec lifecycle.

## Dependencies and Integration Points

It integrates with the server container index, sandbox runtime handler lookup, CRI streaming server helpers, runtime websocket capability, runtime monitor exec serving, gRPC status codes, and kube `remotecommand.TerminalSize`.

## Risks and Edge Cases

`Server.Exec` assumes `s.getSandbox(ctx, c.Sandbox())` returns a sandbox; a nil sandbox would panic when reading `RuntimeHandler`. The stream path maps missing or non-living containers to `codes.NotFound`. The websocket path bypasses the standard streaming endpoint setup, so runtime handler configuration must be correct.

## Test Signals

The tests cover successful endpoint creation, invalid requests, missing containers in the stream callback, living-state checks, stopped containers, and allowing exec setup during graceful termination before the kill loop begins.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec_test.go -->
# sources/cloud-native/cri-o/server/container_exec_test.go

## Purpose

This suite tests CRI exec endpoint setup and the streaming exec callback.

## Important APIs, Types, and Functions

It uses `sut.Exec`, `testStreamService.Exec`, `testContainer.StartExecCmd`, and a local `mockExecStarter` implementing the exec starter interface.

## Control Flow

The tests verify endpoint setup succeeds for a known container and fails for an empty request. Stream tests verify missing containers fail, running containers pass the `Living` gate even if the mock runtime later errors, stopped containers fail the living check, and exec start is allowed while a container is marked stopping but before the kill loop has begun.

## State and Persistence Behavior

State is in the test harness in-memory container and sandbox maps. No persistent files are written.

## Dependencies and Integration Points

The suite depends on CRI types, runtime-spec state constants, remotecommand resize channels, and internal `oci.Container` state behavior.

## Risks and Edge Cases

It does not exercise the websocket runtime-handler path, stdin/stdout/stderr plumbing, tty resize handling, or actual runtime exec success.

## Test Signals

The most important signal is that exec eligibility follows container liveness and termination-state semantics rather than only the high-level CRI request path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_execsync.go -->
# sources/cloud-native/cri-o/server/container_execsync.go

## Purpose

This file implements synchronous CRI command execution inside a container.

## Important APIs, Types, and Functions

`Server.ExecSync(ctx, req)` resolves the container, checks liveness, validates that a command is present, and delegates to `Runtime().ExecSyncContainer`.

## Control Flow

The method starts a tracing/log span, resolves a short container ID, maps missing or non-living containers to gRPC `NotFound`, rejects nil command slices with a plain error, and returns the runtime response including stdout, stderr, and exit code.

## State and Persistence Behavior

No durable state is changed. Runtime exec is transient and bounded by the request timeout passed through to the runtime.

## Dependencies and Integration Points

It integrates with CRI `ExecSyncRequest`, container lookup, container liveness logic, gRPC status codes, and the runtime exec-sync implementation.

## Risks and Edge Cases

The code only rejects `nil` command, not an empty non-nil command slice. Runtime timeout and output-size behavior are delegated. Error typing is mixed: container state errors are gRPC statuses, empty command is a regular error.

## Test Signals

The paired test covers invalid container ID only. Additional coverage should include stopped containers, nil versus empty commands, timeout propagation, runtime errors, and successful stdout/stderr/exit-code mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_execsync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_execsync_test.go -->
# sources/cloud-native/cri-o/server/container_execsync_test.go

## Purpose

This small Ginkgo suite validates an early `ExecSync` failure path.

## Important APIs, Types, and Functions

It calls `sut.ExecSync` with an empty `types.ExecSyncRequest`.

## Control Flow

The test sets up the server harness, sends the invalid request, and expects an error with nil response.

## State and Persistence Behavior

No persistent state is used. The failure happens before runtime execution.

## Dependencies and Integration Points

It depends on the shared server test harness and CRI runtime API types.

## Risks and Edge Cases

Coverage is minimal. It does not validate command validation, living-state checks, timeout behavior, or runtime response mapping.

## Test Signals

The test confirms empty container IDs do not proceed into runtime exec-sync.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_execsync_test.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward.go -->
# sources/cloud-native/cri-o/server/container_portforward.go

## Purpose

This file implements CRI port-forward endpoint creation and the streaming callback that forwards traffic into a pod sandbox network namespace.

## Important APIs, Types, and Functions

`Server.PortForward` prepares a streaming URL with `getPortForward`. `StreamService.PortForward` resolves the sandbox, validates readiness and network namespace path, drains the stream asynchronously on return, and delegates to `Runtime().PortForwardContainer`.

## Control Flow

The unary call only prepares the streaming endpoint and wraps setup failures in a generic error. The stream callback defers stream draining to avoid close/memory issues, resolves the full sandbox ID through `PodIDIndex`, loads the sandbox, verifies it is ready, checks `NetNsPath`, and calls the runtime with the sandbox infra container, namespace path, port, and stream.

## State and Persistence Behavior

No durable state is changed. Stream draining creates a goroutine that copies remaining stream data to `io.Discard`.

## Dependencies and Integration Points

It integrates with CRI streaming helpers, pod sandbox indexes, sandbox readiness and network namespace state, the runtime port-forward implementation, and `go.podman.io/storage/pkg/pools.Copy` for drain behavior.

## Risks and Edge Cases

The unary error hides the underlying `getPortForward` reason. Draining in a goroutine depends on stream behavior and could outlive the request. Missing sandbox, unready sandbox, or empty netns path produce direct errors.

## Test Signals

Tests cover successful endpoint preparation, missing sandbox ID setup failure, and stream callback failure when the sandbox is not found. Runtime forwarding and drain behavior are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward_test.go -->
# sources/cloud-native/cri-o/server/container_portforward_test.go

## Purpose

This suite tests basic port-forward endpoint creation and an early stream failure.

## Important APIs, Types, and Functions

It calls `sut.PortForward` with CRI `PortForwardRequest` and `testStreamService.PortForward`.

## Control Flow

One case requests a streaming endpoint with a sandbox ID and port and expects success. Another omits the sandbox ID and expects setup failure. The stream callback is invoked with a sandbox ID that is not present and should return an error.

## State and Persistence Behavior

Only the in-memory test harness is used. No network namespace or runtime forwarding is established.

## Dependencies and Integration Points

The tests depend on the server test harness and CRI runtime API types.

## Risks and Edge Cases

They do not test sandbox readiness, empty netns paths, stream draining, or successful runtime forwarding.

## Test Signals

The tests confirm that the endpoint setup validates required request fields and that the stream path does not proceed without a resolved sandbox.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove.go -->
# sources/cloud-native/cri-o/server/container_remove.go

## Purpose

This file implements CRI container removal, including idempotency, stopping before removal, runtime/storage cleanup, name/index release, sandbox unlinking, seccomp notifier cleanup, and delete events.

## Important APIs, Types, and Functions

`RemoveContainer` is the CRI RPC. `removeContainerInPod` performs the internal cleanup sequence for a container in a sandbox.

## Control Flow

`RemoveContainer` resolves the container by short ID. If the ID does not exist, it returns success for CRI idempotency; other lookup errors become `NotFound`. It gets the sandbox, calls `removeContainerInPod`, removes any seccomp notifier, emits a deleted event, and returns success. `removeContainerInPod` stops the container if the sandbox is not already stopped, calls NRI remove, deletes the runtime container, removes the exit file, cleans conmon cgroup, deletes storage, releases the name, removes in-memory container state, deletes the truncation ID index entry, and removes the container from the sandbox.

## State and Persistence Behavior

It mutates runtime state, storage state, in-memory server and sandbox maps, name reservation state, ID indexes, seccomp notifier state, conmon cgroups, and the `ContainerExitsDir` exit file. Storage unknown errors during delete are tolerated; index delete errors are returned.

## Dependencies and Integration Points

The code depends on CRI idempotency semantics, containers/storage errors, truncindex errors, runtime delete/stop APIs, storage runtime delete APIs, NRI, sandbox state, OCI container cleanup, and CRI event generation.

## Risks and Edge Cases

Cleanup is sequential; failures before later steps can leave partial state such as released runtime but retained name/index or storage. Stopping before removal uses timeout derived from context. NRI removal warnings do not block cleanup. Seccomp notifier removal is outside `removeContainerInPod`, so callers bypassing `RemoveContainer` must handle it separately.

## Test Signals

Tests cover successful removal of a stopped container, idempotent success for missing IDs, and an error for invalid empty removal. More coverage is useful for runtime/storage delete failures, exit-file errors, and sandbox-stopped behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_linux.go -->
# sources/cloud-native/cri-o/server/container_remove_linux.go

## Purpose

This Linux-specific file closes seccomp notifiers when a container is removed.

## Important APIs, Types, and Functions

`removeSeccompNotifier(ctx, c)` loads a notifier from `s.seccompNotifiers` by container ID, type-asserts it to `*seccomp.Notifier`, and closes it.

## Control Flow

The function is called after container removal. If no notifier exists, it returns. If one exists and is the expected type, `Close` is called and close errors are logged.

## State and Persistence Behavior

It closes kernel/userland seccomp notification resources. The code does not delete the key from `seccompNotifiers`, so lifecycle assumptions depend on notifier close and broader server cleanup.

## Dependencies and Integration Points

It integrates with `setupSeccomp` in container creation, which stores notifiers in `s.seccompNotifiers`, and with the internal `config/seccomp.Notifier` type.

## Risks and Edge Cases

Type assertion failures are silently ignored. The map entry remaining after close could matter if container IDs were reused, though IDs should be unique.

## Test Signals

No direct tests are present for notifier cleanup. Removal tests exercise the caller but not this Linux-specific resource behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_test.go -->
# sources/cloud-native/cri-o/server/container_remove_test.go

## Purpose

This suite tests high-level `RemoveContainer` behavior.

## Important APIs, Types, and Functions

It calls `sut.RemoveContainer`, uses mock runtime delete expectations, sets container state, and manipulates sandbox stopped state to avoid the stop path in the success case.

## Control Flow

The success test creates a stopped container, expects runtime deletion, marks the sandbox stopped, and removes the container. The missing-container test passes a nonexisting ID and expects no error. The invalid request test passes an empty request and expects an error.

## State and Persistence Behavior

State is in-memory plus mock runtime calls. The suite does not assert storage deletion, index deletion, name release, or sandbox list mutation explicitly.

## Dependencies and Integration Points

It depends on gomock runtime server expectations, runtime-spec state, CRI request types, and the shared test harness.

## Risks and Edge Cases

The success case bypasses stop behavior, so pre-remove stop, post-stop cleanup, and NRI interactions are not tested.

## Test Signals

The key signal is CRI idempotency: removing an already missing container returns success.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_unsupported.go -->
# sources/cloud-native/cri-o/server/container_remove_unsupported.go

## Purpose

This non-Linux build-tagged file provides a no-op seccomp notifier cleanup implementation.

## Important APIs, Types, and Functions

`removeSeccompNotifier(ctx, c)` has the same signature as the Linux implementation and returns immediately.

## Control Flow

The shared removal code can call this method unconditionally. On non-Linux platforms there is no seccomp notifier state to close.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It depends only on context and internal `oci.Container` types to satisfy the shared method surface.

## Risks and Edge Cases

If a non-Linux runtime later supports an equivalent notification resource, this no-op would need replacement.

## Test Signals

No direct tests are present; build-tag compilation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log.go -->
# sources/cloud-native/cri-o/server/container_reopen_log.go

## Purpose

This file implements CRI log reopening for a running container, used by log rotation workflows.

## Important APIs, Types, and Functions

`ReopenContainerLog(ctx, req)` resolves a container, verifies runtime liveness, and delegates to `Runtime().ReopenContainerLog`.

## Control Flow

The method starts a span, resolves the short container ID, asks the runtime whether the container is alive, returns an error if not running, and then calls the runtime reopen operation.

## State and Persistence Behavior

It does not mutate CRI-O state directly. The runtime is expected to reopen the log file descriptor, affecting subsequent container log writes.

## Dependencies and Integration Points

It integrates with container lookup, runtime liveness probing, runtime log reopening, and CRI `ReopenContainerLogRequest`.

## Risks and Edge Cases

There is a race between the alive check and runtime reopen. Stopped containers return a generic error. Runtime-specific log path or conmon behavior is delegated.

## Test Signals

The paired test covers invalid container ID. Additional tests should cover not-running containers, liveness check errors, runtime reopen errors, and successful reopen.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log_test.go -->
# sources/cloud-native/cri-o/server/container_reopen_log_test.go

## Purpose

This suite validates an early failure path for log reopening.

## Important APIs, Types, and Functions

It calls `sut.ReopenContainerLog` with an empty `types.ReopenContainerLogRequest`.

## Control Flow

The test sets up the server and expects the empty request to fail during container lookup.

## State and Persistence Behavior

No state is persisted or changed.

## Dependencies and Integration Points

It depends on the shared server test harness and CRI runtime API types.

## Risks and Edge Cases

Coverage is minimal and does not exercise running-state validation or runtime reopen behavior.

## Test Signals

The test confirms invalid IDs are rejected before runtime log operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore.go -->
# sources/cloud-native/cri-o/server/container_restore.go

## Purpose

This file implements container creation from checkpoint archives or checkpoint OCI images. It is used when `CreateContainer` detects an image input that represents checkpoint data and prepares an `oci.Container` flagged for later restore in `StartContainer`.

## Important APIs, Types, and Functions

`checkIfCheckpointOCIImage(ctx, input)` resolves an image and checks for CRI-O checkpoint annotations. `CRImportCheckpoint(ctx, createConfig, sb, sandboxUID)` imports checkpoint metadata, reconstructs a CRI container config, validates required bind mounts, reserves name/ID state, calls the normal `createSandboxContainer`, and marks the new container as restore-capable.

## Control Flow

Restore import validates image and metadata fields. If input resolves to a checkpoint OCI image, it rejects namespace-specific signature policy, mounts the image through the storage image server, and defers unmount. Otherwise it opens a checkpoint archive, extracts selected metadata files into a temp directory, and defers cleanup. It reads `spec.dump` and `config.dump`, unmarshals original annotations from the dumped spec, updates pod UID and container hash where applicable, checks sandbox stop state, creates a new factory container, chooses the rootfs image from `RootfsImageRef` or `RootfsImageName`, applies incoming resources/security context and dumped masked/readonly paths, verifies every non-ignored bind mount in the dump is present in the new CRI request, creates sandbox config, reserves the name, sets restore mode, invokes common creation, adds indexes and in-memory state, marks created/restore, records archive path or storage image ID and checkpoint time, and returns the new ID.

## State and Persistence Behavior

It may mount/unmount a checkpoint OCI image, create/remove a temp extraction directory, reserve/release container names, create storage/runtime bundle state via `createSandboxContainer`, add/remove in-memory containers and ID indexes on failure, and set restore metadata on the `oci.Container`. Context cancellation returns an error after construction but does not use the same resource-store handoff pattern as normal create.

## Dependencies and Integration Points

The code depends on checkpointctl metadata file names, containers/storage archive extraction, internal annotations, image status and storage image mount APIs, signature policy namespace context, sandbox state, the factory container and shared creation pipeline, kubelet pod UID labels, and runtime restore in `StartContainer`.

## Risks and Edge Cases

Security-sensitive behavior includes refusing undeclared bind mounts from checkpoint data and rejecting namespaced signature policies for OCI checkpoint restores. Archive parsing trusts checkpoint metadata structure and fails on missing or malformed JSON. Ignored mounts are recreated for the new environment. Cleanup is defer-heavy; missing cleanup can leave mounted images, temp dirs, name reservations, storage containers, or ID indexes. The typo in a comment is harmless.

## Test Signals

Restore tests cover missing archives, empty/non-tar archives, broken `spec.dump`/`config.dump`, empty metadata, successful archive restore with rootfs image by name or ID, bind mount preservation, annotation hash/pod UID update, and OCI checkpoint image mount failure behavior. CRIU availability and rootless mode gate some tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore_test.go -->
# sources/cloud-native/cri-o/server/container_restore_test.go

## Purpose

This Ginkgo suite exercises checkpoint restore import behavior from archives and OCI checkpoint images.

## Important APIs, Types, and Functions

It calls `sut.CRImportCheckpoint`, sets checkpoint restore configuration, uses CRIU availability checks, creates temporary tar archives with checkpoint metadata files, and sets gomock expectations on image/storage/runtime servers.

## Control Flow

Failure cases cover nonexistent archives, empty archives, invalid tar data, malformed `spec.dump`, missing or malformed annotations, broken `config.dump`, and OCI checkpoint image mount paths missing metadata. Success cases build archives containing spec annotations, mounts, masked/readonly paths, and config with either `rootfsImageName` or `rootfsImageRef`, then expect storage container creation/start and graph root access.

## State and Persistence Behavior

The tests write and remove local files such as `archive.tar`, `spec.dump`, and `config.dump`, and use temporary graph roots. Mock expectations stand in for persistent storage/runtime mutations.

## Dependencies and Integration Points

The suite depends on checkpoint-restore/go-criu, containers/storage archive utilities, runtime-spec and image-spec types, internal storage reference parsers, kubelet labels, and gomock.

## Risks and Edge Cases

Some tests skip without CRIU or when rootless. They validate many parse and validation branches but do not perform a real runtime restore; `StartContainer` restore behavior is covered separately only at a high level.

## Test Signals

The suite is a strong signal that restore import rejects malformed checkpoint inputs and enforces bind mount declaration instead of blindly trusting checkpoint metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start.go -->
# sources/cloud-native/cri-o/server/container_start.go

## Purpose

This file implements CRI `StartContainer`, including normal runtime start and checkpoint restore start.

## Important APIs, Types, and Functions

`StartContainer(ctx, req)` resolves the container, branches on restore mode, runs runtime-handler hooks and NRI notifications, starts the runtime container, emits a CRI started event, and persists final state.

## Control Flow

For restore containers, it calls `ContainerRestore` with the container ID and empty checkpoint options. On restore failure it reloads the container, releases its name, deletes storage, removes in-memory state, and returns the error. For normal containers, it requires internal state `ContainerStateCreated`, retrieves the sandbox and hooks, sends NRI start, defers failure cleanup that sets start failure fields, runs pre-stop/NRI stop/remove cleanup, and always writes state to disk. It runs pre-start hooks, calls runtime `StartContainer`, generates a started event, sends NRI post-start, logs details, and returns success.

## State and Persistence Behavior

It mutates runtime state from created to running, writes container state to disk, may remove a failed container and its storage, releases names after failed restore, emits CRI events, and updates container status fields on start failure.

## Dependencies and Integration Points

It integrates with checkpoint restore metadata, runtime start and restore APIs, runtime-handler hooks, NRI, sandbox lookup, storage runtime deletion, CRI event generation, and `oci.Container` state helpers.

## Risks and Edge Cases

The logged PID comes from `state := c.State()` captured before runtime start, so it may not reflect the post-start PID unless runtime updates the same state object. Failure cleanup after normal start attempts removal in pod, which can cascade through stop/delete paths. Restore cleanup is separate and must remain aligned with import state.

## Test Signals

Tests cover invalid ID and invalid/non-created state. Successful start, hooks, NRI, restore success/failure, CRI event emission, and persisted state behavior need broader integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start_test.go -->
# sources/cloud-native/cri-o/server/container_start_test.go

## Purpose

This suite checks early `StartContainer` validation failures.

## Important APIs, Types, and Functions

It calls `sut.StartContainer` with known and empty container IDs using the shared test harness.

## Control Flow

Cases create a container that is not in created state and expect `StartContainer` to fail, and pass an empty request to expect lookup failure.

## State and Persistence Behavior

Only in-memory test state is used. Runtime start is not invoked in these tests.

## Dependencies and Integration Points

It depends on CRI `StartContainerRequest` and the shared server test setup.

## Risks and Edge Cases

Coverage does not include successful start, start failure cleanup, hooks, events, NRI calls, or restore mode.

## Test Signals

The tests confirm the start path enforces a created-state precondition.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats.go -->
# sources/cloud-native/cri-o/server/container_stats.go

## Purpose

This file implements unary CRI stats lookup for a single container.

## Important APIs, Types, and Functions

`ContainerStats(ctx, req)` resolves a container by short ID, resolves its sandbox, and returns `s.StatsForContainer(container, sb)`.

## Control Flow

The method starts a span, looks up the container, errors on missing IDs, loads the sandbox from the container's sandbox ID, returns an explicit error if the sandbox is missing, and wraps the computed stats in `ContainerStatsResponse`.

## State and Persistence Behavior

It reads in-memory container and sandbox state plus whatever live cgroup/runtime data `StatsForContainer` reads. It does not mutate state.

## Dependencies and Integration Points

It integrates with container lookup, sandbox lookup, CRI stats protobufs, and the server stats implementation.

## Risks and Edge Cases

Stats accuracy and nil fields are delegated to `StatsForContainer`. A missing sandbox for an existing container is treated as an error, surfacing inconsistent server state.

## Test Signals

Tests cover invalid container lookup. List-stats tests cover stopped-container filtering separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stats.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop.go -->
# sources/cloud-native/cri-o/server/container_stop.go

## Purpose

This file implements CRI container stopping, including idempotency, runtime-handler hooks, NRI stop notification, storage unmount, and state persistence.

## Important APIs, Types, and Functions

`StopContainer(ctx, req)` is the CRI RPC. `stopContainer(ctx, ctr, timeout)` performs the stop. `postStopCleanup(ctx, ctr, sb, hooks)` unmounts storage, runs post-stop hooks, sends NRI stop, and persists state.

## Control Flow

The RPC resolves the container by short ID. Missing IDs return success for CRI idempotency if the truncation index reports not-exist; other lookup errors become `NotFound`. It then calls `stopContainer`. The internal function retrieves the sandbox and hooks, runs `PreStop`, calls runtime `StopContainer` with the timeout, then runs cleanup. Cleanup attempts storage stop/unmount, logs post-stop hook errors without failing, sends NRI stop, and writes container state to disk last.

## State and Persistence Behavior

Runtime state changes to stopped through the runtime, storage is unmounted via storage runtime server, NRI state may be updated, and container state is persisted to disk after post-stop cleanup. No name/index removal happens here.

## Dependencies and Integration Points

It depends on CRI idempotency semantics, truncindex errors, runtime stop API, storage runtime stop API, runtime-handler hooks, NRI, sandbox lookup, and `ContainerStateToDisk`.

## Risks and Edge Cases

Pre-stop hook errors abort stopping. Post-stop hook and storage unmount errors are logged but do not prevent the response if runtime stop succeeded. Persisting state last avoids reporting stopped before cleanup but means a crash during cleanup can leave disk state stale.

## Test Signals

Tests cover a successful stop path with a mock runtime stop and idempotent success for a missing ID. They do not cover hook errors, storage unmount failures, NRI behavior, or timeout handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop_test.go -->
# sources/cloud-native/cri-o/server/container_stop_test.go

## Purpose

This suite tests high-level `StopContainer` behavior.

## Important APIs, Types, and Functions

It calls `sut.StopContainer`, sets container state, and expects mock runtime `StopContainer`.

## Control Flow

The success case creates a container, sets stopped state, expects runtime stop, and calls the RPC. The idempotency case passes a nonexisting ID and expects no error.

## State and Persistence Behavior

State is in-memory plus mocked runtime behavior. The tests do not inspect disk state persistence.

## Dependencies and Integration Points

They depend on gomock, runtime-spec state, CRI stop requests, and the shared harness.

## Risks and Edge Cases

The tests do not exercise pre/post hooks, storage unmount, NRI stop, or timeout propagation.

## Test Signals

The key signal is that CRI stop is idempotent for already removed or unknown containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources.go -->
# sources/cloud-native/cri-o/server/container_update_resources.go

## Purpose

This file implements CRI `UpdateContainerResources`, translating CRI Linux resource updates to OCI runtime resources and updating CRI-O's stored resource view.

## Important APIs, Types, and Functions

`UpdateContainerResources(ctx, req)` validates container state, allows NRI mutation of requested resources, validates memory updates, calls runtime update, updates internal stored resources, and sends NRI post-update. `toOCIResources` converts CRI CPU, memory, and cgroup v2 unified fields to `rspec.LinuxResources`. `reapplySharedCPUs` merges OpenShift shared CPUs into requested cpusets.

## Control Flow

The RPC resolves a container and requires it to be running or created. If Linux resources are present, it reapplies shared CPUs from `OPENSHIFT_SHARED_CPUS`, calls NRI update, defaults to the original resources if NRI returns nil, validates the new memory limit, converts resources to OCI, calls runtime `UpdateContainer`, updates CRI-O's resource store, and runs NRI post-update. If no Linux section is present, it returns success without mutation.

## State and Persistence Behavior

Runtime cgroup resources are updated through the runtime. CRI-O updates the in-memory/stored Linux resources associated with the container via `UpdateContainerLinuxResources`. The request object can be mutated in place by `reapplySharedCPUs`.

## Dependencies and Integration Points

It depends on CRI Linux resource types, OpenContainers runtime spec resources, cgroup v2 detection, cgroup memory swap support, NRI update hooks, runtime update API, and Kubernetes cpuset parsing.

## Risks and Edge Cases

`strings.Split(env, "=")` assumes env strings contain `=`, which is normally true but could panic for malformed spec env entries. Shared CPU merge mutates `req.Linux.CpusetCpus`. Memory validation is platform-specific and can be skipped when stats are unavailable. Swap is set equal to memory limit only when memory swap cgroup support exists.

## Test Signals

Tests cover success with nil Linux resources, CPU field conversion, cgroup v2 unified fields, invalid state, invalid IDs, and NRI-enabled success. They do not cover shared CPU merge or memory validation failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_linux.go -->
# sources/cloud-native/cri-o/server/container_update_resources_linux.go

## Purpose

This Linux-specific file validates memory limit decreases before applying container resource updates.

## Important APIs, Types, and Functions

`validateMemoryUpdate(ctx, c, newMemoryLimit)` checks negative limits, treats zero as unlimited, reads current stats through `StatsForContainer`, and rejects limits below current memory usage.

## Control Flow

Negative limits return an error. Zero returns success. The function resolves the sandbox; if missing, it logs a warning and allows the update. It retrieves stats; if stats or usage bytes are missing, it logs and allows the update. Otherwise it compares the requested limit with current usage and errors if the limit is lower.

## State and Persistence Behavior

No state is mutated. It reads live/container stats and gates the later runtime update in `UpdateContainerResources`.

## Dependencies and Integration Points

It integrates with sandbox lookup, stats generation, CRI memory usage fields, logging, and the main resource update flow.

## Risks and Edge Cases

Validation is best-effort: missing sandbox or stats allows potentially unsafe decreases. Current usage can change after validation before runtime update, so this is not a hard race-free guarantee. Negative limits are always rejected.

## Test Signals

No direct tests in this subset cover memory validation. Resource update tests exercise the caller but not below-current-usage rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_test.go -->
# sources/cloud-native/cri-o/server/container_update_resources_test.go

## Purpose

This suite tests CRI resource update behavior and resource conversion.

## Important APIs, Types, and Functions

It calls `sut.UpdateContainerResources`, sets `testContainer` spec/state, inspects updated `specs.LinuxResources`, and covers NRI-enabled setup.

## Control Flow

Tests verify success with no Linux resources, CPU period/quota/shares and cpuset updates, unified cgroup v2 map updates when running on cgroup v2, error on invalid container state, error on invalid/empty IDs, and success when NRI is enabled.

## State and Persistence Behavior

The tests mutate the in-memory container spec and state. They inspect the container spec after update to confirm stored resource changes.

## Dependencies and Integration Points

They depend on CRI resource types, runtime-spec resources, internal cgroup detection, mock runtime setup, NRI config, and shared harness helpers.

## Risks and Edge Cases

The suite does not test memory limit validation, runtime update errors, shared CPU environment merge, NRI returning modified resources, or post-update NRI failures.

## Test Signals

The strongest signal is that successful resource updates are reflected in the container's stored OCI resources, not only sent to the runtime.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_unsupported.go -->
# sources/cloud-native/cri-o/server/container_update_resources_unsupported.go

## Purpose

This non-Linux file provides basic memory update validation for platforms without Linux cgroups.

## Important APIs, Types, and Functions

`validateMemoryUpdate(ctx, c, newMemoryLimit)` rejects negative memory limits and otherwise returns success.

## Control Flow

There is a single branch: negative values error, zero or positive values pass. Context and container parameters are unused except for signature compatibility.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform-specific validation hook used by `UpdateContainerResources` on non-Linux builds.

## Risks and Edge Cases

Because there are no cgroups, it cannot validate current usage or enforce cgroup semantics. Runtime update support may still fail later.

## Test Signals

No direct tests are present; build-tag compilation and generic update tests are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/health.go -->
# sources/cloud-native/cri-o/server/health.go

## Purpose

This file implements CRI-O health checking through a self-CRI status call and asynchronous CNI readiness gating.

## Important APIs, Types, and Functions

`checkCRIHealth(ctx, timeout)` creates a remote runtime client to CRI-O's own socket, calls `Status`, validates runtime conditions, and handles NetworkReady specially. `cniPluginReadinessCheck(ctx)` starts a one-time goroutine that waits for CNI readiness and flips the package-level atomic `cniPluginInitialized`.

## Control Flow

The health check opens a remote runtime service, defers close, requests runtime status, rejects nil status or nil conditions, starts the CNI readiness check, then iterates conditions. A false `NetworkReady` condition is ignored until CNI has been initialized at least once; other false conditions return an error with message and reason.

## State and Persistence Behavior

State is process-global: `cniPluginInitialized` and `cniInitOnce`. No disk state is written. The readiness goroutine logs success or failure and stores readiness in the atomic flag.

## Dependencies and Integration Points

It depends on `k8s.io/cri-client`, server listen socket config, runtime status conditions, CNI plugin readiness via `waitForCNIPlugin`, and logging.

## Risks and Edge Cases

Global once/atomic state means readiness is process-wide, not per server instance. If the first readiness goroutine fails, `cniInitOnce` prevents retry through this path, leaving NetworkReady ignored only while the atomic remains false but without another checker starting. Health depends on CRI-O being able to connect to its own socket.

## Test Signals

No tests are included in this subset. Useful coverage would mock remote status conditions and CNI readiness transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info.go -->
# sources/cloud-native/cri-o/server/image_fs_info.go

## Purpose

This file implements CRI image filesystem usage reporting for image and container storage roots.

## Important APIs, Types, and Functions

`ImageFsInfo` retrieves the storage image server store and calls `getStorageFsInfo`. `getStorageFsInfo(store)` determines graph and image paths and returns CRI filesystem usage entries. `getUsage(containerPath)` calls `utils.GetDiskUsageStats` and wraps bytes/inodes in CRI types.

## Control Flow

When `store.ImageStore()` is empty, graph root is treated as shared image/container storage under `<graphRoot>/<driver>-images`, and the same usage is returned for both image and container filesystems. When image store is separate, container usage is read from `<graphRoot>/<driver>-containers` and image usage from `<imageStore>/<driver>-images`.

## State and Persistence Behavior

The code reads filesystem usage stats and current time only. It does not mutate storage.

## Dependencies and Integration Points

It depends on containers/storage `Store`, CRI `ImageFsInfoResponse`, and CRI-O utility disk usage stats.

## Risks and Edge Cases

Path construction assumes driver-specific directory names. Missing or inaccessible directories return errors. Timestamps are generated per `getUsage`, so image and container entries can have slightly different times.

## Test Signals

Tests cover successful shared graph root usage and failure on invalid image directory. Separate image store behavior is not covered in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info_test.go -->
# sources/cloud-native/cri-o/server/image_fs_info_test.go

## Purpose

This suite tests image filesystem usage reporting.

## Important APIs, Types, and Functions

It calls `sut.ImageFsInfo`, mocks storage store methods, creates a test directory, and checks returned filesystem entry counts.

## Control Flow

The success case sets graph root and image store to empty, graph driver to `test`, creates `test-images`, and expects one image and one container filesystem entry. The failure case leaves the driver name empty and expects an error.

## State and Persistence Behavior

The test creates and removes a local directory. Store behavior is mocked.

## Dependencies and Integration Points

It depends on gomock store expectations, the server harness, and filesystem access.

## Risks and Edge Cases

It does not test separate image store paths, inodes values, or permission errors.

## Test Signals

The tests confirm path construction for the shared storage-root case and that invalid storage paths surface errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list.go -->
# sources/cloud-native/cri-o/server/image_list.go

## Purpose

This file implements CRI image listing and streaming, including normal container images and OCI artifacts exposed as CRI images.

## Important APIs, Types, and Functions

`ListImages`, `StreamImages`, and `listImages` provide unary and chunked stream APIs. `ConvertImage` converts internal `storage.ImageResult` to CRI `types.Image`.

## Control Flow

For an image filter with a non-empty image spec, `listImages` reuses `storageImageStatus` to return at most the matching storage image, then also attempts artifact status and appends the artifact CRI image if found. Without a filter, it lists all storage images, converts each, lists artifacts, logs artifact-list errors as warnings, and appends artifact images. Streaming chunks the list by `streamChunkSize`.

## State and Persistence Behavior

The file reads image and artifact stores only. It does not mutate storage.

## Dependencies and Integration Points

It integrates with storage image status/list APIs, artifact store status/list APIs, CRI image protobufs, shared image status helper, and stream chunking.

## Risks and Edge Cases

Filter semantics are lookup-like, not broad label/query filtering, because kubelet historically does not use filters. Artifact status errors other than not-found are logged in filtered mode but do not fail the whole request after a storage image match. `ConvertImage` falls back to `PreviousName@Digest` when repo digests are missing.

## Test Signals

Tests cover list success, filter success, list error, filter status error, and `ConvertImage` behavior for nil input, repo tags/digests, numeric user, and previous-name digest fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list_test.go -->
# sources/cloud-native/cri-o/server/image_list_test.go

## Purpose

This suite tests image listing and image conversion behavior.

## Important APIs, Types, and Functions

It calls `sut.ListImages` and `server.ConvertImage`, using mocked image server calls and parsed storage image references/IDs.

## Control Flow

List tests cover unfiltered success, filtered success through short-name resolution and image status, image list failure, and filtered status failure. Conversion tests cover empty tags/digests, tags and digests with size and numeric user, previous name plus digest fallback, and nil input.

## State and Persistence Behavior

No real image storage is mutated. Mock image server responses drive the results.

## Dependencies and Integration Points

The suite depends on gomock, OpenContainers digest, internal storage reference parsing, and CRI image types.

## Risks and Edge Cases

Artifact listing/status paths are not explicitly tested. Streaming list chunking is also not covered.

## Test Signals

The tests lock down the CRI conversion shape, especially user-to-UID handling and previous-name digest fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull.go -->
# sources/cloud-native/cri-o/server/image_pull.go

## Purpose

This file implements CRI `PullImage`, including authentication handling, concurrent pull deduplication, namespace-specific policy/auth context, decryption keys, optional separate cgroup pulls, progress timeout/metrics, artifact fallback, and Docker auth decoding.

## Important APIs, Types, and Functions

`PullImage` prepares `pullArguments` and deduplicates in-progress pulls through `pullOperationsInProgress`. `pullImage` creates a namespace-aware image system context, handles namespaced auth files, chooses cgroup settings, resolves short names, and tries pull candidates. `contextForNamespace`, `prepareTempAuthFile`, `pullImageCandidate`, `resolveImageRefToID`, `consumeImagePullProgress`, `tryIncrementImagePullFailureMetric`, `tryRecordSkippedMetric`, and `decodeDockerAuth` support the flow.

## Control Flow

The RPC extracts image, sandbox cgroup, namespace, and auth. Docker `auth` is base64-decoded into username/password if present. A locked map ensures only one goroutine pulls a specific `pullArguments` tuple while others wait on its waitgroup. The active pull uses namespace signature policy, optionally consumes a namespaced credential-provider auth file by renaming it into an `in-use` directory and cleaning it after pull, applies explicit credentials, reads decryption config, validates separate-pull-cgroup systemd requirements, resolves short-name candidates, and pulls each candidate until one succeeds. Candidate pulls set up a progress channel and cancellation goroutine that cancels when no progress arrives within configured timeout. Successful pulls increment success metrics and resolve the pulled repo digest to a storage image ID or artifact CRI ID.

## State and Persistence Behavior

State includes the in-memory pull operation map, `storage.ImageBeingPulled`, metrics counters/histograms, temporary namespaced auth-file moves/removals, pulled image/artifact storage, and optional cgroup creation in storage copy options. The panic guard initializes pull errors so waiters do not observe a false success after panic.

## Dependencies and Integration Points

The file integrates with CRI auth and sandbox config, containers/image system context and progress types, CRI-O credential provider auth file naming, storage image server pull/status APIs, artifact store status, ocicrypt decryption keys, registry error descriptors, metrics, signature policies, short-name resolution, and systemd cgroup configuration.

## Risks and Edge Cases

Deduplication key includes credentials, namespace, cgroup, and image, so similar pulls with different auth are separate. Namespaced auth file consumption intentionally races for same normalized image names; kubelet retry is expected to recover. Progress timeout begins only after progress events because the timer is initially stopped. `decodeDockerAuth` treats malformed decoded strings without `:` as empty credentials. Separate pull cgroup is systemd-only and validates `.slice` names except pod cgroup mode. Artifact resolution after pull depends on artifact store status if image storage lookup fails.

## Test Signals

Tests cover successful pull returning image ID, credential decode errors, pull errors, and short-name resolution errors. Additional coverage should include concurrent deduplication, namespaced auth file movement/cleanup, progress timeout cancellation, artifact ID resolution, metrics labels, and separate cgroup validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull_test.go -->
# sources/cloud-native/cri-o/server/image_pull_test.go

## Purpose

This suite tests core `PullImage` success and failure paths.

## Important APIs, Types, and Functions

It calls `sut.PullImage`, uses mocked `CandidatesForPotentiallyShortImageName`, `PullImage`, and `ImageStatusByName`, and uses parsed storage references and IDs.

## Control Flow

The success test resolves a short image name, pulls a repo digest, looks that digest up in storage, and expects the response image ref to be the storage image ID. Failure tests cover invalid base64 auth, storage pull errors, and candidate resolution errors for empty image input.

## State and Persistence Behavior

No real images are pulled. The in-memory pull deduplication map is exercised but not asserted directly.

## Dependencies and Integration Points

The tests depend on gomock image server expectations, CRI image/auth types, and internal storage reference parsers.

## Risks and Edge Cases

They do not cover duplicate concurrent pulls, credential-provider auth files, progress timeout, artifact resolution, or separate pull cgroups.

## Test Signals

The tests confirm that CRI `PullImageResponse.ImageRef` returns the resolved image ID, not merely the pulled named reference.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove.go -->
# sources/cloud-native/cri-o/server/image_remove.go

## Purpose

This file implements CRI `RemoveImage` for storage images and OCI artifacts, including CRI idempotency and protection for image volumes currently used by containers.

## Important APIs, Types, and Functions

`RemoveImage(ctx, req)` validates an image spec and delegates to `removeImage`. `removeImage(ctx, imageRef)` handles ID deletion, name untagging, artifact removal, and idempotent not-found behavior. `volumeInUse(digest)` scans container volumes to prevent removing images used as mounted image volumes.

## Control Flow

If the ref resolves as an image ID prefix, the code checks image volume usage and calls storage `DeleteImage`, treating unknown/not-an-image as success. Otherwise it resolves candidate names, looks up status, checks volume usage by image ID, un-tags the first candidate that succeeds, and handles concurrent deletion errors idempotently. It then checks the artifact store for the original ref; not-found is success, other status errors fail, and found artifacts are usage-checked by digest and removed.

## State and Persistence Behavior

The code mutates image storage by deleting or untagging images and mutates artifact storage by removing artifacts. It reads current containers and their volumes to avoid deleting mounted volume images.

## Dependencies and Integration Points

It depends on storage image server ID/name resolution, containers/storage error types, artifact store status/remove, container list state, CRI image spec, and internal `oci.ContainerVolume` image fields.

## Risks and Edge Cases

Only the first successfully untagged candidate is removed. If storage untag succeeds and artifact removal later fails, storage state has already changed. `volumeInUse` assumes `volume.Image` is non-nil; if any volume lacks an image pointer, this can panic. It does not check normal container rootfs image use because storage handles that case.

## Test Signals

Tests cover name removal, full-ID deletion, untag errors, name resolution errors, missing image spec, idempotency for unknown/not-an-image delete, and concurrent deletion during untag. Artifact and volume-in-use paths are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove_test.go -->
# sources/cloud-native/cri-o/server/image_remove_test.go

## Purpose

This suite tests image removal behavior for storage images.

## Important APIs, Types, and Functions

It calls `sut.RemoveImage` and mocks image server methods for ID prefix resolution, candidate resolution, status, delete, and untag.

## Control Flow

Tests verify name-based untag success, full image ID deletion success, untag failure, candidate resolution failure, validation failure for empty image, idempotent success when full-ID delete reports unknown image, idempotent success when delete reports not-an-image, and idempotent success when untag reports not-an-image after concurrent deletion.

## State and Persistence Behavior

No real image storage is mutated. Mock expectations model storage behavior.

## Dependencies and Integration Points

The suite depends on containers/storage error types, gomock, CRI image request types, and internal storage reference/ID parsing.

## Risks and Edge Cases

It does not test artifact removal or image-volume in-use checks. It also does not assert container rootfs in-use behavior because storage owns that check.

## Test Signals

The suite strongly confirms CRI idempotency around image removal races and already-deleted images.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status.go -->
# sources/cloud-native/cri-o/server/image_status.go

## Purpose

This file implements CRI image status lookup for storage images and OCI artifacts, plus image user parsing and verbose image info.

## Important APIs, Types, and Functions

`ImageStatus(ctx, req)` validates image input, checks storage image status, falls back to artifact status, and builds `types.ImageStatusResponse`. `storageImageStatus(ctx, spec)` resolves an image by ID prefix or short-name candidates. `getUserFromImage`, `createImageInfo`, and `isHexString` support conversion and error handling.

## Control Flow

Image status rejects missing image specs. Storage lookup first tries heuristic ID-prefix resolution and calls `ImageStatusByID`. If that is not applicable, it resolves potential short-name candidates and tries `ImageStatusByName` until one succeeds, ignoring no-such-image and returning the last non-notfound error. If short-name resolution fails for a string that looks like a hex ID/digest of length at least 3, it returns not found instead of surfacing the resolver error. If storage status is nil, artifact status is attempted; found artifacts are returned as CRI images, not-found returns an empty response, and other errors are logged. Verbose storage responses include labels and OCI config JSON.

## State and Persistence Behavior

The file reads image and artifact stores only. It does not mutate storage.

## Dependencies and Integration Points

It depends on containers/image storage errors, containers/storage errors, internal storage image server APIs, artifact store APIs, goccy JSON, OpenContainers image spec, CRI image/status types, and shared storage reference parsing behavior.

## Risks and Edge Cases

Unknown images return an empty successful response, matching CRI expectations. Hex-looking resolver failures are suppressed to avoid confusing ID-prefix lookups. `getUserFromImage` ignores groups after `:` and treats numeric users as UID. Artifact errors after storage miss are logged but not returned except when found path succeeds.

## Test Signals

Tests cover normal status, verbose info JSON, full ID lookup, unknown image success, storage status error, short-name resolution error, and missing image validation. Artifact fallback and hex resolver suppression are not directly covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status_test.go -->
# sources/cloud-native/cri-o/server/image_status_test.go

## Purpose

This suite tests storage-backed CRI image status behavior.

## Important APIs, Types, and Functions

It calls `sut.ImageStatus`, mocks image server resolution/status methods, and uses parsed storage references and IDs.

## Control Flow

Tests verify normal short-name status, verbose status with OCI image config JSON, full image ID status, unknown image returning an empty successful response, status retrieval errors, short-name resolution errors, and missing image validation.

## State and Persistence Behavior

All storage interactions are mocked. No real image state is changed.

## Dependencies and Integration Points

The suite depends on gomock, containers/image no-such-image errors, OpenContainers image spec, CRI image status requests, and internal storage parsing helpers.

## Risks and Edge Cases

Artifact fallback, image user parsing variations, and hex-like resolver suppression are not covered.

## Test Signals

The tests confirm CRI-compatible not-found behavior: unknown images return a successful response without an image instead of an error.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status_test.go -->
