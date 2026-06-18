# Research: subset-b-000067

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create_linux_test.go

## Purpose
This Linux-focused test suite validates CRI container OCI spec generation for security, namespaces, mounts, process identity, devices, CDI injection, cgroup behavior, and Linux-specific compatibility rules. It shares `getCreateContainerTestData` with generic create tests but extends it with Linux `SecurityContext`, resource, and namespace assertions.

## Important APIs, Types, and Functions
Key tests include `TestContainerCapabilities`, `TestContainerSpecTty`, `TestContainerSpecDefaultPath`, `TestContainerSpecReadonlyRootfs`, `TestContainerSpecWithExtraMounts`, `TestContainerAndSandboxPrivileged`, `TestPrivilegedBindMount`, `TestCgroupNamespace`, `TestMountPropagation`, `TestPidNamespace`, `TestUserNamespace`, `TestMaskedAndReadonlyPaths`, `TestHostname`, `TestProcessUser`, `TestNonRootUserAndDevices`, `TestPrivilegedDevices`, `TestBaseOCISpec`, `TestCDIInjections`, and `TestUserNamespaceWithHostNetwork`. It exercises `buildContainerSpec`, `platformSpecOpts`, `opts.WithMounts`, `customopts.WithCDI`, and OCI spec structures.

## Control Flow, State, and Persistence
The tests build synthetic CRI container/sandbox/image configs, invoke spec construction, and inspect the resulting in-memory OCI spec. Temporary files are used for `/etc/passwd`, `/etc/group`, and CDI YAML specs; no containerd runtime is started. Fake OS hooks simulate mount lookup and hostname behavior. User namespace tests also ensure sandbox and container namespace configs must match.

## Dependencies and Integration Points
Coverage spans Linux capability sets, SELinux labels, cgroup v1/v2 namespace selection, mount propagation validation, host/pod/container PID namespace wiring, supplemental group policies, base runtime specs, CDI registry configuration, device ownership, and privileged runtime toggles. It ties CRI API fields to OCI runtime-spec output.

## Risks and Test Signals
Primary risks are privilege escalation, invalid namespace combinations, host mount propagation misuse, incorrect user/group merging, CDI injection drift, device ownership regressions, and host-network plus userns `/sys` mount failures. Strong signals are exact spec field comparisons, expected errors for invalid namespace/idmap inputs, and platform-gated cgroup assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_other.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create_other.go

## Purpose
This non-Linux/non-Windows build-tagged file supplies portable no-op create helpers so the CRI server package compiles on other platforms. It provides the platform hooks used by `createContainer`.

## Important APIs, Types, and Functions
`containerSpecOpts` returns an empty `[]oci.SpecOpts`; `snapshotterOpts` returns an empty `[]snapshots.Opt`. Both accept the same CRI/image config parameters as platform implementations.

## Control Flow, State, and Persistence
There is no side effect, validation, or persistence. Calls are pass-through defaults used after generic spec construction has selected a supported platform branch.

## Dependencies and Integration Points
The file depends only on CRI runtime config types, OCI spec option type, image config, and snapshot options. It integrates with `platformSpecOpts` and `createContainer` as the fallback implementation for Darwin/other build targets.

## Risks and Test Signals
The risk is under-validation on unsupported or partially supported platforms: security profiles, snapshot idmaps, and Windows rootfs labels are intentionally absent. The paired `container_create_other_test.go` verifies the portable test data and expected generic annotations/mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_other_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create_other_test.go

## Purpose
This non-Linux/non-Windows test fixture provides `getCreateContainerTestData` for generic create tests on other platforms. It validates only the cross-platform portions of generated specs.

## Important APIs, Types, and Functions
The file defines `getCreateContainerTestData` and references `checkMount` to satisfy shared test compilation. The returned `specCheck` validates process args, working directory, environment merging, bind mount options, and default CRI annotations.

## Control Flow, State, and Persistence
No runtime state is persisted. Tests using this helper build synthetic CRI configs and compare an in-memory OCI spec. The helper deliberately avoids Linux or Windows-only fields.

## Dependencies and Integration Points
It integrates with generic tests in `container_create_test.go` by providing platform-specific fixture data under the `!windows && !linux` build tag. It uses runtime API metadata, image-spec config, and runtime-spec mounts.

## Risks and Test Signals
The main signal is that generic create behavior continues to compile and assert core annotations on alternative platforms. Risk is limited coverage: security contexts, platform resources, and snapshot options are outside this file’s scope.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_other_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create_test.go

## Purpose
This cross-platform suite validates generic container spec construction and helper behavior shared by Linux, Windows, and other builds. It focuses on CRI-to-OCI command resolution, annotations, image-defined volumes, base runtime specs, and Linux system-file mounts where available.

## Important APIs, Types, and Functions
Important helpers and tests include `checkMount`, `TestGeneralContainerSpec`, `TestPodAnnotationPassthroughContainerSpec`, `TestContainerSpecCommand`, `TestVolumeMounts`, `TestContainerAnnotationPassthroughContainerSpec`, `TestBaseRuntimeSpec`, and `TestLinuxContainerMounts`.

## Control Flow, State, and Persistence
Tests construct fake CRI configs, call `buildContainerSpec`, `runtimeSpec`, or `volumeMounts`, and assert in-memory OCI spec output. `TestBaseRuntimeSpec` uses a fake runtime service with a base OCI JSON spec and confirms the loaded base is deep-copied, not mutated. Linux mount tests use fake OS stat behavior to simulate sandbox files.

## Dependencies and Integration Points
The suite covers `customopts.WithProcessArgs`, passthrough annotation matching, image volume deduplication against CRI mounts, Linux idmap propagation to generated volumes, base runtime spec loading, cgroup path correction, and sandbox files such as `/etc/hostname`, `/etc/hosts`, `/etc/resolv.conf`, and `/dev/shm`.

## Risks and Test Signals
Risks include command/args precedence regressions, annotation leakage or omission, non-absolute Linux image volume paths, incorrect userns idmap propagation, accidental base-spec mutation, and missing sandbox mount compatibility. Signals are exact mount, env, annotation, and cgroup path checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create_windows.go

## Purpose
This Windows-specific create helper supplies platform hooks used during container creation. It adds snapshot labels for Windows rootfs sizing and otherwise leaves extra per-platform OCI spec options empty.

## Important APIs, Types, and Functions
`containerSpecOpts` returns no extra `oci.SpecOpts` on Windows. `snapshotterOpts` reads `config.GetWindows().GetResources().GetRootfsSizeInBytes()` and, when nonzero, returns a snapshot label `containerd.io/snapshot/windows/rootfs.sizebytes`.

## Control Flow, State, and Persistence
There is no persistent state in this file. Snapshot labels flow into `customopts.WithNewSnapshot` during `createContainer`, affecting the writable layer prepared by the selected snapshotter.

## Dependencies and Integration Points
The file integrates CRI Windows resource limits with containerd snapshot service options. It depends on runtime API Windows resources, snapshot labels, and OCI option types.

## Risks and Test Signals
The key risk is snapshotter-specific label drift or rootfs quota silently not applying. Windows spec behavior is mostly covered in `container_create_windows_test.go`; rootfs-size label behavior would need snapshotter-level or option inspection coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_windows_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create_windows_test.go

## Purpose
This Windows test fixture and suite validates Windows CRI container spec generation, including process command formatting, mounts, network namespace, HostProcess constraints, resources, credentials, and annotations.

## Important APIs, Types, and Functions
It defines `getSandboxConfig` and Windows `getCreateContainerTestData`. Tests include `TestContainerWindowsNetworkNamespace`, `TestMountCleanPath`, `TestMountNamedPipe`, `TestHostProcessRequirements`, and `TestEntrypointAndCmdForArgsEscaped`.

## Control Flow, State, and Persistence
Tests call `buildContainerSpec` with synthetic CRI configs and inspect only the in-memory OCI spec. No hcsshim runtime is started. The entrypoint test table varies image `Entrypoint`, `Cmd`, `ArgsEscaped`, CRI `Command`, and CRI `Args` to verify `Process.Args` versus `Process.CommandLine`.

## Dependencies and Integration Points
The file integrates CRI Windows resources with `spec.Windows.Resources`, Windows network namespace setting, mount path normalization, named pipe mount preservation, HostProcess pod/container consistency, credential spec forwarding, username selection, affinity CPU handling, and default CRI annotations.

## Risks and Test Signals
Risks include malformed Windows command lines, unsafe HostProcess mixing, incorrect path normalization for drive paths or named pipes, lost credential specs, and missing HNS namespace wiring. Signals are exact command-line/args checks and hard errors when HostProcess settings differ between pod and container.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_events.go -->
# sources/cloud-native/containerd/internal/cri/server/container_events.go

## Purpose
This file implements the CRI `GetContainerEvents` streaming RPC by forwarding events from the service’s container event queue to the gRPC stream.

## Important APIs, Types, and Functions
`(*criService).GetContainerEvents` subscribes to `c.containerEventsQ`, defers closing the subscription, and calls `s.Send(event)` for each event received.

## Control Flow, State, and Persistence
The method is a long-running stream. Its only state is the queue subscription and stream backpressure/error handling. It exits when the queue channel closes or when `Send` returns an error.

## Dependencies and Integration Points
It integrates with lifecycle methods that call `generateAndSendContainerEvent`, including create, start, remove, and exit handling. The public contract is Kubernetes CRI event streaming.

## Risks and Test Signals
Risks are missed close cleanup, stream error propagation, and queue backpressure. There are no direct tests in this subset; event generation is indirectly exercised by lifecycle code paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_exec.go -->
# sources/cloud-native/containerd/internal/cri/server/container_exec.go

## Purpose
This file implements the streaming CRI `Exec` request setup. It validates container existence and running state, then asks the stream server to allocate an exec endpoint.

## Important APIs, Types, and Functions
`(*criService).Exec` reads `runtime.ExecRequest`, looks up the container in `containerStore`, records tracing attributes, checks `cntr.Status.Get().State()`, and returns `c.streamServer.GetExec(r)`.

## Control Flow, State, and Persistence
No task is created here; this only prepares a streaming endpoint. Runtime execution happens later through the streaming server and shared exec internals. State checks prevent exec against created/exited/unknown containers.

## Dependencies and Integration Points
It integrates CRI streaming, tracing, container store lookup, and status state conversion. `container_execsync.go` contains the lower-level exec process implementation used by synchronous and streaming paths.

## Risks and Test Signals
Risks include allowing exec into non-running containers or leaking ambiguous container lookup errors. This subset lacks a direct `Exec` test, so behavior is mainly protected through shared store/status conventions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_execsync.go -->
# sources/cloud-native/containerd/internal/cri/server/container_execsync.go

## Purpose
This file implements synchronous CRI exec, including bounded stdout/stderr collection, process creation inside an existing task, TTY handling, timeouts, IO attachment, and cleanup.

## Important APIs, Types, and Functions
Key types/functions are `cappedWriter`, `ExecSync`, `execOptions`, `execInternal`, `execInContainer`, and `drainExecSyncIO`. It uses containerd `Task.Exec`, `Process.Wait`, `Process.Start`, `Process.Kill`, `Process.Delete`, CRI IO helpers, and optional streaming IO endpoints.

## Control Flow, State, and Persistence
`ExecSync` caps each output stream at 16 MiB and calls `execInContainer`. The shared exec path loads the container spec/task, adjusts process args and TTY env, creates fifo or streaming IO based on runtime config, waits for the exec process, starts it, attaches IO, handles terminal resize, applies timeout cancellation with SIGKILL, drains IO, and deletes the process on exit. No durable container metadata is changed.

## Dependencies and Integration Points
The code integrates CRI runtime config, sandbox endpoints, container store, sandbox store, containerd task/process APIs, `remotecommand` terminal sizing, tracing, and `DrainExecSyncIOTimeout`.

## Risks and Test Signals
Risks include goroutine leaks when `Start` fails, unbounded output, hanging on inherited pipe descriptors from child processes, timeout cleanup races, and command-line leakage from stale `CommandLine`. Tests cover `cappedWriter` semantics and `drainExecSyncIO` timeout/delete behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_execsync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_execsync_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_execsync_test.go

## Purpose
This unit test file validates helper behavior around synchronous exec output truncation and IO draining after exec process exit.

## Important APIs, Types, and Functions
Tests are `TestCWWrite`, `TestCWClose`, and `TestDrainExecSyncIO`. The local `fakeExecProcess` implements `containerd.Process` enough to record method calls such as `Delete`.

## Control Flow, State, and Persistence
`TestCWWrite` writes past the remaining byte cap and confirms the caller still receives full write counts while the underlying buffer is capped. `TestDrainExecSyncIO` uses timed channel closure to distinguish normal attach completion from timeout-driven process deletion. State is in-memory only.

## Dependencies and Integration Points
The tests depend on `cioutil.NewNopWriteCloser`, containerd process interfaces, and wall-clock timers. They directly exercise helper contracts used by `ExecSync`.

## Risks and Test Signals
The important signal is that output truncation is silent to the writer, matching CRI response-size behavior, and that stuck IO triggers `Delete` with process kill. Timer-based tests can be slow or flaky if durations are too tight, but the chosen values are broad.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_execsync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount.go -->
# sources/cloud-native/containerd/internal/cri/server/container_image_mount.go

## Purpose
This file implements CRI image-volume mounts. It mutates CRI mount entries that reference an image into host bind mounts backed by unpacked image snapshots and cleans those snapshots when the sandbox is removed.

## Important APIs, Types, and Functions
Key functions are `mutateMounts`, `ensureLeaseExist`, `mutateImageMount`, `cleanupImageMounts`, and `ensureImageSubPath`. They use containerd images, leases, snapshot services, mount helpers, platform resolution, `identity.ChainID`, and CRI mount image fields.

## Control Flow, State, and Persistence
`mutateMounts` ensures a sandbox lease and calls `mutateImageMount` for each extra mount. Image mounts must have empty host path, be readonly, and specify an image. The code resolves and unpacks the image, prepares a snapshot at a sandbox/image-specific host path, mounts it, optionally validates a directory `ImageSubPath` with `os.OpenInRoot`, assigns `HostPath`, and clears UID/GID mappings after snapshot idmap options have been applied. Cleanup unmounts, removes snapshots, and deletes image-volume directories.

## Dependencies and Integration Points
It integrates CRI OCI volume source semantics, containerd image service, snapshotter selection, sandbox leases, platform-specific mount detection, Linux idmap snapshot labels, and sandbox cleanup.

## Risks and Test Signals
Risks include path traversal through subpaths, non-readonly image mounts, stale mounted snapshots, idmap double-application, lease loss, and cleanup impacting old pods. Linux snapshot option tests cover idmap label generation; subpath safety relies on `OpenInRoot`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux.go

## Purpose
This Linux-specific image-volume helper optimizes overlay cleanup, detects real mountpoints, and converts CRI user namespace ID mappings into snapshot remapper labels.

## Important APIs, Types, and Functions
`addVolatileOptionOnImageVolumeMount` appends `volatile` to overlay mounts on kernels >= 5.10 unless already present. `ensureImageVolumeMounted` checks `os.Stat` and `mount.Lookup` to verify the target itself is the mountpoint. `getImageVolumeSnapshotOpts` parses UID/GID mappings and returns `containerd.WithRemapperLabels`.

## Control Flow, State, and Persistence
Kernel volatile support is cached via `sync.Once`. Mount detection distinguishes an existing directory from an actual mountpoint. Snapshot options are returned only when both UID and GID mappings exist; the first mapping drives remapper labels.

## Dependencies and Integration Points
It depends on containerd mount/snapshot APIs, kernel version detection, CRI runtime mount ID mappings, and Linux user namespace parsing helpers. It is called by `mutateImageMount` before preparing image-volume snapshots.

## Risks and Test Signals
Risks include incorrect kernel feature detection, treating plain directories as mounted volumes, and wrong idmap label selection. `container_image_mount_linux_test.go` checks remapper labels, empty mappings, partial mappings, and multi-line mapping rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux_test.go

## Purpose
This Linux-only test file validates snapshot option generation for image-volume mounts under user namespaces.

## Important APIs, Types, and Functions
`TestGetImageVolumeSnapshotOpts` covers `getImageVolumeSnapshotOpts`; `optsToInfo` applies returned `snapshots.Opt` values into a `snapshots.Info` for label comparison.

## Control Flow, State, and Persistence
The test constructs CRI `runtime.Mount` values with UID/GID mapping combinations, invokes the helper, and compares generated remapper labels. It also confirms the helper does not clear mappings on the mount object, because clearing is the responsibility of `mutateImageMount` after snapshot preparation.

## Dependencies and Integration Points
It depends on `containerd.WithRemapperLabels`, snapshot info labels, CRI ID mappings, and Linux build tags. It protects the image-volume/userns integration path.

## Risks and Test Signals
Risks include accepting unsupported multi-line idmaps, dropping mappings too early, or failing to idmap image volumes. Signals are exact label equality and expected errors for multiple UID mapping lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount_other.go -->
# sources/cloud-native/containerd/internal/cri/server/container_image_mount_other.go

## Purpose
This non-Linux image-volume helper provides portable behavior for platforms without Linux overlay volatile mounts or snapshot idmap remapper labels.

## Important APIs, Types, and Functions
`addVolatileOptionOnImageVolumeMount` is a no-op. `ensureImageVolumeMounted` treats any existing target path as mounted. `getImageVolumeSnapshotOpts` returns nil.

## Control Flow, State, and Persistence
The file performs only an existence check and returns default options. It does not inspect mount tables or mutate snapshot labels.

## Dependencies and Integration Points
It depends on `os.Stat`, containerd mount/snapshot types, and CRI mounts. It integrates with `mutateImageMount` as the `!linux` implementation.

## Risks and Test Signals
Risk is weaker mounted-state detection on non-Linux platforms, because an existing directory is considered sufficient. There are no direct tests in this subset; platform-specific runtime integration would be needed to validate non-Linux image volumes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_image_mount_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_list.go -->
# sources/cloud-native/containerd/internal/cri/server/container_list.go

## Purpose
This file implements the CRI `ListContainers` RPC and conversion from internal container store entries to CRI container summaries.

## Important APIs, Types, and Functions
Key functions are `ListContainers`, `toCRIContainer`, `normalizeContainerFilter`, and `filterCRIContainers`. It uses `containerStore`, `sandboxStore`, CRI `ContainerFilter`, and `runtime.Container` fields.

## Control Flow, State, and Persistence
`ListContainers` reads all containers from the in-memory/checkpoint-backed store, converts them, normalizes short IDs through store lookups, applies ID/sandbox/state/label filters, records a timer, and returns the list. It does not mutate container state except that `normalizeContainerFilter` rewrites the request filter object to canonical IDs.

## Dependencies and Integration Points
It integrates CRI list semantics with container store state derivation. `ImageRef` and `ImageId` both use the stored platform-specific image config digest for backward compatibility and garbage collection without doing image-store lookups.

## Risks and Test Signals
Risks include surprising mutation of filter input, short-ID ambiguity, stale image reference semantics, and label matching drift. `container_list_test.go` covers conversion, filter combinations, and truncated container/sandbox IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_list_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_list_test.go

## Purpose
This test file validates container list conversion and filter semantics for the CRI server.

## Important APIs, Types, and Functions
Tests include `TestToCRIContainer`, `TestFilterContainers`, and `TestListContainers`. `containerForTest` helps create store entries with fake status.

## Control Flow, State, and Persistence
The tests populate fake sandbox and container stores, invoke either direct conversion/filter helpers or `ListContainers`, and assert returned CRI containers. In-memory store state models created, running, and exited containers through timestamp fields.

## Dependencies and Integration Points
It covers container store, sandbox store, short ID normalization, CRI states, labels, metadata, and the choice to set `ImageId` equal to stored `ImageRef` in list responses.

## Risks and Test Signals
Signals are exact output containers for no filter, ID, sandbox ID, state, label, and mixed filters. Risks include tests depending on list ordering and incomplete coverage for ambiguous short IDs or image-store lookups, which `ListContainers` intentionally avoids.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_log_reopen.go -->
# sources/cloud-native/containerd/internal/cri/server/container_log_reopen.go

## Purpose
This file implements CRI log reopening for running containers, used after external log rotation.

## Important APIs, Types, and Functions
`(*criService).ReopenContainerLog` looks up the container, verifies it is running, calls `createContainerLoggers`, replaces the `"log"` output in container IO, and closes previous stdout/stderr writers.

## Control Flow, State, and Persistence
The method mutates the container’s IO output registry. It does not restart tasks or change container status. If the container is not running, it returns an error before touching log writers.

## Dependencies and Integration Points
It integrates CRI log rotation, container store status, `ContainerIO.AddOutput`, and log file creation logic from `container_start.go`.

## Risks and Test Signals
Risks include closing active writers incorrectly, failing to close old log files, and reopening logs for non-running containers. There are no direct tests in this subset; behavior is tied to `createContainerLoggers` and runtime IO integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_log_reopen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_remove.go -->
# sources/cloud-native/containerd/internal/cri/server/container_remove.go

## Purpose
This file implements CRI `RemoveContainer`, including idempotent not-found handling, forced stop of running/unknown containers, NRI notification, containerd deletion, checkpoint/root cleanup, store removal, name release, and delete event generation.

## Important APIs, Types, and Functions
Key functions are `RemoveContainer`, `setContainerRemoving`, and `resetContainerRemoving`. It uses `containerStore`, `containerNameIndex`, containerd `Container.Delete(WithSnapshotCleanup)`, `ensureRemoveAll`, NRI hooks, and tracing/timers.

## Control Flow, State, and Persistence
Removal first resolves store metadata and containerd info. If containerd metadata is missing, the CRI store entry and name index are cleaned. Running or unknown containers are force-stopped with timeout 0. `setContainerRemoving` prevents concurrent start/remove. On success the containerd container, checkpoint, root dir, volatile root dir, store entry, and name reservation are removed; on failure `Removing` is reset.

## Dependencies and Integration Points
It integrates with stop logic, NRI plugin synchronization, container checkpoint persistence, snapshot cleanup, lifecycle events, and metrics.

## Risks and Test Signals
Risks include races with start, leaked root directories, name-index leaks, non-idempotent not-found behavior, and NRI failures masking removal. `container_remove_test.go` covers the `Removing` guard state; full deletion behavior needs integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_remove_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_remove_test.go

## Purpose
This unit test file validates the container removal state guard.

## Important APIs, Types, and Functions
`TestSetContainerRemoving` exercises `setContainerRemoving` and `resetContainerRemoving` against fake container store statuses.

## Control Flow, State, and Persistence
Each case creates an in-memory container with a synthetic status. Running, starting, and already removing containers should error without metadata changes. Exited containers can enter `Removing` and then reset.

## Dependencies and Integration Points
It depends on `containerstore.NewContainer`, fake statuses, and timestamp-derived CRI state logic. It protects the concurrency gate used by `RemoveContainer`.

## Risks and Test Signals
The signal is exact preservation of status on failed guard transitions. The test does not cover filesystem cleanup, containerd deletion, or NRI interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start.go -->
# sources/cloud-native/containerd/internal/cri/server/container_start.go

## Purpose
This file implements CRI `StartContainer`, including normal task start, checkpoint restore, IO/log setup, status transition, NRI lifecycle hooks, exit monitoring, and log writer creation.

## Important APIs, Types, and Functions
Key functions are `StartContainer`, `setContainerStarting`, `resetContainerStarting`, and `createContainerLoggers`. It uses containerd `NewTask`, `Restore`, `Task.Wait`, `Task.Start`, `startContainerExitMonitor`, NRI hooks, `updateContainerIOOwner`, and CRI loggers.

## Control Flow, State, and Persistence
Start looks up container metadata/info, sets `Starting`, checks sandbox readiness, creates log-backed IO, and either restores a checkpoint or creates a new task. On failure it writes exit status metadata with error reason/message and resets `Starting`. On success it records PID/start time, starts an exit monitor, sends a started event, and calls post-start hooks. Restore mode also deletes checkpoint artifacts after success. Log creation opens the CRI log path when configured and wires stdout/stderr, or discards output if logging is disabled.

## Dependencies and Integration Points
It integrates container store status, sandbox store readiness, runtime handler/path/endpoints, user namespace IO ownership, streaming/fifo IO, checkpoint restore metadata, NRI, tracing, metrics, and CRI eventing.

## Risks and Test Signals
Risks include races with remove, leaked tasks on start failure, incorrect failed-start state, log file leaks, restore artifact cleanup errors, and invalid target PID namespaces. `container_start_test.go` covers the `Starting` guard; Linux/other platform files cover IO owner options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/container_start_linux.go

## Purpose
This Linux-specific start helper adjusts task creation options so IO fifo ownership matches the container process user when user namespaces are active.

## Important APIs, Types, and Functions
`updateContainerIOOwner` reads the container OCI spec, builds a `userns.IDMap`, maps `spec.Process.User` to host IDs, and returns `containerd.WithUIDOwner` and `containerd.WithGIDOwner` task options.

## Control Flow, State, and Persistence
The helper returns nil unless the config is Linux and user namespace mode is not node. It validates `spec.Linux` and `spec.Process`, computes host IDs, and supplies options used by `container.NewTask`.

## Dependencies and Integration Points
It depends on CRI user namespace options, runtime-spec UID/GID mappings, `internal/userns`, and containerd task options. It is called by `StartContainer` before task creation.

## Risks and Test Signals
Risks include invalid specs, mismatched user namespace mappings, and IO permission failures for rootless/idmapped containers. There is no direct unit test in this subset; related user namespace spec tests increase confidence in mapping setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start_other.go -->
# sources/cloud-native/containerd/internal/cri/server/container_start_other.go

## Purpose
This non-Linux start helper provides a no-op `updateContainerIOOwner` implementation for platforms where Linux user namespace fifo ownership does not apply.

## Important APIs, Types, and Functions
`updateContainerIOOwner` accepts the same context, containerd container, and CRI container config as the Linux version and returns nil task options and nil error.

## Control Flow, State, and Persistence
No state is read or mutated. The helper exists for build compatibility and platform separation.

## Dependencies and Integration Points
It depends only on containerd task option and CRI config types. It integrates with `StartContainer`, which appends the returned options before creating a task.

## Risks and Test Signals
The risk is platform-specific IO ownership requirements emerging without implementation here. There are no direct tests; compilation and start path integration provide the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_start_test.go

## Purpose
This unit test file validates the container starting state guard used by `StartContainer`.

## Important APIs, Types, and Functions
`TestSetContainerStarting` exercises `setContainerStarting` and `resetContainerStarting` with fake container statuses.

## Control Flow, State, and Persistence
Each test creates an in-memory container status. Only created containers may enter `Starting`; running, exited, unknown, already-starting, or removing containers return an error and leave status unchanged. Successful cases reset the flag afterward.

## Dependencies and Integration Points
It depends on container store status state derivation from timestamps and protects the lifecycle gate that prevents concurrent start/remove races.

## Risks and Test Signals
The strong signal is exact metadata preservation on failed transitions. The test does not exercise task creation, logging, NRI, or checkpoint restore behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_start_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stats.go -->
# sources/cloud-native/containerd/internal/cri/server/container_stats.go

## Purpose
This file implements CRI `ContainerStats` for one container. It fetches task metrics by container ID and converts the single result into CRI stats.

## Important APIs, Types, and Functions
`(*criService).ContainerStats` uses `containerStore.Get`, containerd `TaskService().Metrics`, `tasks.MetricsRequest`, `getMetricsHandler`, and the platform-specific metrics decoder returned by `container_stats_list.go`.

## Control Flow, State, and Persistence
The method resolves the canonical container ID, requests exactly one metric with filter `id==<id>`, rejects responses that do not contain exactly one metric, obtains a handler based on sandbox platform/runtime, decodes metrics, and returns `runtime.ContainerStatsResponse`. It may update CPU usage history through shared stats conversion helpers.

## Dependencies and Integration Points
It integrates single-container CRI stats with the same Linux/Windows conversion pipeline used by list stats, snapshot writable-layer accounting, sandbox platform detection, and containerd task metrics.

## Risks and Test Signals
Risks include metrics response cardinality mismatch, unsupported sandbox platforms, missing task metrics for stopped containers, and conversion errors. Direct tests are in `container_stats_list_test.go` for shared helpers rather than this thin RPC wrapper.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stats_list.go -->
# sources/cloud-native/containerd/internal/cri/server/container_stats_list.go

## Purpose
This file implements CRI `ListContainerStats` and the core conversion of containerd task metrics into CRI CPU, memory, IO, PID, and writable-layer stats for Linux and Windows containers.

## Important APIs, Types, and Functions
Key functions/types are `ListContainerStats`, `listContainerStats`, `containerStats`, `metricsHandler`, `getMetricsHandler`, `toContainerStats`, `toCRIContainerStats`, `getUsageNanoCores`, `normalizeContainerStatsFilter`, `buildTaskMetricsRequest`, `matchLabelSelector`, `windowsContainerMetrics`, `linuxContainerMetrics`, `getWorkingSet`, `getWorkingSetV2`, `getAvailableBytes`, `getAvailableBytesV2`, `convertCg2PSIToCRI`, `cpuContainerStats`, `memoryContainerStats`, and `ioContainerStats`.

## Control Flow, State, and Persistence
The list path builds a metrics request from filters, calls containerd task metrics, maps metrics by ID, obtains/caches a metrics handler per sandbox, decodes platform metrics, calculates instantaneous CPU nano cores, and returns CRI stats. CPU rate state persists in the background stats collector when available or in container/sandbox store `Stats` history as a fallback. Snapshot store data supplies writable-layer bytes and inodes.

## Dependencies and Integration Points
Dependencies include cgroup v1/v2 stats, hcsshim Windows stats, containerd task metrics API, typeurl protobuf unpacking, sandbox platform service, runtime snapshotter selection, image filesystem paths, snapshot store, and CRI stats models.

## Risks and Test Signals
Risks include wrong cgroup v1/v2 type handling, rate calculation on first sample or counter rollback, unsupported platforms, nil metrics, missing snapshots, and PSI unit conversion. Tests cover CPU nano-core deltas, working set/available-byte math, memory conversion, platform metrics data, and skipped containers when stores are incomplete.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stats_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stats_list_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_stats_list_test.go

## Purpose
This test file validates the shared stats conversion logic for CPU, memory, available bytes, working set, and partial list conversion behavior.

## Important APIs, Types, and Functions
Tests include `TestContainerMetricsCPUNanoCoreUsage`, `TestGetWorkingSet`, `TestGetWorkingSetV2`, `TestGetAvailableBytes`, `TestGetAvailableBytesV2`, `TestContainerMetricsMemory`, and `TestListContainerStats`. Helpers include `uint64Ptr` and `platformBasedMetricsData`.

## Control Flow, State, and Persistence
The tests use `newTestCRIService`, fake containers/sandboxes, synthetic cgroup v1/v2 and Windows metric payloads, and timestamp deltas. CPU nano-core tests verify first-sample nil, normal deltas, counter rollback, and store update behavior.

## Dependencies and Integration Points
It exercises cgroup stats structures, hcsshim stats on Windows, typeurl marshaling, platform defaults, container/sandbox stores, and CRI stats structures. It covers the platform-sensitive data consumed by `ContainerStats` and `ListContainerStats`.

## Risks and Test Signals
Signals are exact numerical expectations for memory working set, available bytes, RSS/page faults, and CPU rates. Test gaps include full task service RPC behavior, writable-layer snapshot accounting, and PSI conversion assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stats_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status.go -->
# sources/cloud-native/containerd/internal/cri/server/container_status.go

## Purpose
This file implements CRI `ContainerStatus` and conversion of internal container metadata/status into CRI status and optional verbose JSON info.

## Important APIs, Types, and Functions
Key functions/types are `ContainerStatus`, `toCRIContainerStatus`, `ContainerInfo`, and `toCRIContainerInfo`. It uses image store lookup, `util.ParseImageReferences`, container spec/info, runtime options extraction, and platform-specific `toCRIContainerUser`.

## Control Flow, State, and Persistence
`ContainerStatus` resolves the container, derives image tag/ref semantics from the image store when available, preserves local image config digest as `ImageId`, converts internal status, fills missing `CreatedAt` from containerd info, and optionally marshals verbose `ContainerInfo`. The conversion maps timestamps by state, derives default exit reasons, includes mounts/log path/resources/user/stop signal, and serializes runtime spec/runtime metadata for verbose mode.

## Dependencies and Integration Points
It integrates container store metadata, image store references, containerd container spec/info, runtime options, CRI stop-signal conversion, platform user extraction, and Kubernetes CRI status fields.

## Risks and Test Signals
Risks include image reference compatibility for multi-arch images, zero CreatedAt rejection, verbose JSON failures, stop-signal mapping drift, and losing user data on platform helper errors. `container_status_test.go` covers state/reason/image/ref conversion and verbose false behavior; Linux user tests cover user extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/container_status_linux.go

## Purpose
This Linux-specific status helper extracts the runtime user from a container’s OCI spec and converts it into CRI `LinuxContainerUser`.

## Important APIs, Types, and Functions
`toCRIContainerUser` checks the embedded containerd container, loads `Container.Spec(ctx)`, reads `spec.Process.User`, and returns UID, GID, and supplemental groups.

## Control Flow, State, and Persistence
No state is mutated. If the container handle is nil or spec loading fails, an error is returned to the caller; `toCRIContainerStatus` logs and falls back to an empty user when this happens. If `Process` is nil, the helper returns an empty `ContainerUser`.

## Dependencies and Integration Points
It depends on containerd container spec retrieval, runtime-spec process user fields, and CRI Linux user fields. It is called during `ContainerStatus`.

## Risks and Test Signals
Risks include failure to report the actual runtime user, incorrect supplemental group type conversion, and noisy status failures. `container_status_linux_test.go` covers nil container, spec error, missing process, and additional GID conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_status_linux_test.go

## Purpose
This Linux-only test file validates `toCRIContainerUser`.

## Important APIs, Types, and Functions
`TestToCRIContainerUser` uses `fakeSpecOnlyContainer` from `container_status_test.go` and container store wrappers to check user extraction paths.

## Control Flow, State, and Persistence
The table covers nil embedded container, spec retrieval error, no `Process`, no additional groups, and additional groups. All data is in-memory OCI spec data.

## Dependencies and Integration Points
It depends on containerd container interface fakes, runtime-spec `Process.User`, CRI `ContainerUser`, and Linux build tags. It protects the status response user field.

## Risks and Test Signals
Signals are exact expected errors and exact UID/GID/supplemental group conversion. The test does not cover how `toCRIContainerStatus` logs and suppresses these errors, only the helper itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_other.go -->
# sources/cloud-native/containerd/internal/cri/server/container_status_other.go

## Purpose
This non-Linux/non-Windows helper returns an empty CRI container user for platforms without a platform-specific user mapping implementation.

## Important APIs, Types, and Functions
`toCRIContainerUser` accepts context and container metadata but returns `&runtime.ContainerUser{}` and nil error.

## Control Flow, State, and Persistence
There is no side effect or spec lookup. The function is a build-tagged compatibility implementation.

## Dependencies and Integration Points
It integrates with `toCRIContainerStatus`, ensuring status construction can compile and return a user field on other platforms.

## Risks and Test Signals
The risk is loss of user reporting on platforms where it could become meaningful. There are no direct tests in this subset; behavior is intentionally minimal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_status_test.go

## Purpose
This test file validates CRI status conversion, image reference behavior, verbose-info disabling, stop-signal conversion, and supporting fakes for container/image services.

## Important APIs, Types, and Functions
Tests include `TestToCRIContainerStatus`, `TestToCRIContainerInfo`, `TestContainerStatus`, and `TestToCRISignal`. Helpers/fakes include `getContainerStatusTestData`, `fakeImageService`, `patchExceptedWithState`, and `fakeSpecOnlyContainer`.

## Control Flow, State, and Persistence
The tests create fake container metadata/status, fake image references with both tag and digest, and fake container specs. They call conversion functions and the `ContainerStatus` RPC wrapper, then compare exact CRI status output. `TestToCRISignal` covers standard and real-time signal names, plus fallback for unknown strings.

## Dependencies and Integration Points
It exercises container store, image store, runtime-spec fakes, snapshot/image service interface shape, CRI status fields, and stop-signal conversion used by status responses.

## Risks and Test Signals
Signals are exact state/timestamp/reason mapping, image tag/digest/config-digest semantics, and broad signal name coverage. Gaps include verbose true JSON serialization and live containerd spec/info failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/container_status_windows.go

## Purpose
This Windows-specific status helper currently returns an empty CRI container user.

## Important APIs, Types, and Functions
`toCRIContainerUser` has the same signature as other platform implementations and returns `&runtime.ContainerUser{}`.

## Control Flow, State, and Persistence
No containerd spec lookup or mutation occurs. Windows user details are not surfaced through this CRI field by this implementation.

## Dependencies and Integration Points
It integrates with generic `toCRIContainerStatus` on Windows builds and depends only on CRI runtime types.

## Risks and Test Signals
Risk is limited observability for Windows run-as user in CRI status. There are no direct tests in this subset; Windows create tests cover username selection in the OCI spec.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_status_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop.go -->
# sources/cloud-native/containerd/internal/cri/server/container_stop.go

## Purpose
This file implements CRI `StopContainer`, including idempotence, graceful stop signal selection, timeout fallback to SIGKILL, unknown-state cleanup, shim connection retry, NRI stop notification, and wait helpers.

## Important APIs, Types, and Functions
Key functions are `StopContainer`, `stopContainerRetryOnConnectionClosed`, `stopContainer`, `waitContainerStop`, and `cleanupUnknownContainer`. It uses containerd task APIs, container status channels, CRI stop-signal helpers, image stop signal fallback, NRI, event monitor handling, and tracing/timers.

## Control Flow, State, and Persistence
The RPC returns success for missing containers. Running/unknown containers are stopped; other states return success without action. Unknown tasks get an exit monitor so cleanup can reuse normal exit handling. With positive timeout, a CRI-configured signal, stored metadata signal, image stop signal, or SIGTERM is sent once using an atomic guard; if the container does not stop before the deadline, SIGKILL is sent and the method waits for `container.Stopped()`. Unknown cleanup synthesizes a `TaskExit` event with unknown exit code.

## Dependencies and Integration Points
It integrates with container store status, image service, containerd task wait/kill, shim ttrpc retry detection, NRI sync blocking, lifecycle event handling, CRI stop signal conversion, and metrics.

## Risks and Test Signals
Risks include double-sending graceful signals, leaving unknown containers uncleaned, mishandling deleted images, context timeout races, and shim closed retry behavior. `container_stop_test.go` covers wait behavior and signal conversion helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop_signal.go -->
# sources/cloud-native/containerd/internal/cri/server/container_stop_signal.go

## Purpose
This helper file converts between CRI enum signal names and OCI/runtime signal strings, including real-time signal names that encode plus/minus signs in enum identifiers.

## Important APIs, Types, and Functions
`criSignalToOCIStopSignal` converts `runtime.Signal` to strings and returns an invalid-argument wrapped error for unknown enum values. `convertFromCRISignal` changes `PLUS`/`MINUS` markers to `+`/`-`. `toCRISignal` performs the reverse for status reporting and returns `RUNTIME_DEFAULT` for unknown strings.

## Control Flow, State, and Persistence
The functions are pure string/enum transforms with no state. Runtime default maps to an empty OCI stop signal on outbound conversion.

## Dependencies and Integration Points
It depends on generated CRI signal name/value maps and `errdefs.ErrInvalidArgument`. It is used during create validation, stop signal selection, and status reporting.

## Risks and Test Signals
Risks include invalid signal acceptance, real-time signal mangling, and status defaulting hiding unsupported image signals. `container_stop_test.go` and `container_status_test.go` cover runtime default, standard signals, real-time plus/minus conversion, unknown enum errors, and unknown string fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop_signal.go -->
