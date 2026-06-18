# subset-b-000069 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri_other.go -->
# sources/cloud-native/containerd/internal/cri/server/nri_other.go

## Purpose

This non-Linux build-tag file provides placeholder CRI implementation methods for NRI-adjacent container operations that are implemented differently on Linux. It keeps the server package compiling on non-Linux platforms without wiring Linux-specific resource update or stop logic.

## Important APIs, Types, and Functions

`(*criImplementation).UpdateContainerResources` accepts a container store object, CRI update request, and current status, but returns an empty status with no error. `(*criImplementation).StopContainer` accepts a container and timeout and returns nil without performing work.

## Control Flow

Both methods are straight-line stubs. There is no validation, containerd call, NRI notification, status mutation, or timeout handling.

## State and Persistence Behavior

No state is read or persisted. The empty status returned by `UpdateContainerResources` is risky if accidentally used as real state on a non-Linux path.

## Dependencies and Integration Points

The file depends only on CRI container store types and CRI runtime API request types. It integrates through build tags with platform-specific CRI implementation method sets.

## Risks and Test Signals

The main risk is silent no-op behavior on unsupported platforms. Compile coverage for non-Linux targets is the primary signal; behavioral tests should assert that callers either avoid these paths or treat them as unsupported where appropriate.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/controller.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/controller.go

## Purpose

This file registers the `podsandbox` sandbox controller plugin and defines the controller's core state and event-wait behavior for pause-container-backed Kubernetes pod sandboxes. It is the bridge between containerd's generic `sandbox.Controller` interface and CRI's pod sandbox metadata, store, warning, and event-monitor facilities.

## Important APIs, Types, and Functions

`Controller` holds CRI runtime/image config, a containerd client, warning service, OS abstraction, pod sandbox event monitor, and an in-memory `Store`. `init` registers the plugin with event, lease, sandbox-store, transfer, CRI, service, and warning dependencies. `Platform` returns the default OCI platform. `Wait` waits on a cached `types.PodSandbox`. `Update` is currently a no-op. `waitSandboxExit` converts a task wait result into a `TaskExit` event. `handleSandboxTaskExit` deletes the pause task and marks the sandbox exited.

## Control Flow

Plugin initialization builds an in-memory-services client, retrieves CRI runtime and image service configs, creates the controller, starts an event monitor, and returns the controller. Runtime exit handling waits on the task channel, converts failures to exit code 255, applies a timeout for delete/status mutation, and uses event-monitor backoff when cleanup fails.

## State and Persistence Behavior

The controller stores live pod sandbox objects only in memory. Durable metadata is carried elsewhere in containerd sandbox/container extensions. Exit handling mutates the sandbox status to not-ready and releases waiters through the `PodSandbox` stop channel.

## Dependencies and Integration Points

It integrates with containerd plugin registration, CRI service plugins, the warning service, `events.EventMonitor`, `containerd.Task` deletion, protobuf timestamp conversion, and the pod sandbox store types.

## Risks and Test Signals

Risks include missed cleanup if the in-memory store lacks an entry, blocked serialized event handling, and current `Update` no-op behavior. Controller tests cover basic status access; broader signals come from sandbox lifecycle, recovery, and event monitor integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/controller_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/controller_test.go

## Purpose

This test file supplies a minimal controller fixture and verifies controller status translation for an in-memory pod sandbox.

## Important APIs, Types, and Functions

`newControllerService` builds a `Controller` with test config, real OS abstraction, and a fresh store. `Test_Status` saves a `PodSandbox` with a known ID and `StateReady`, calls `Status`, and asserts the returned `ControllerStatus` carries the sandbox ID and string state.

## Control Flow

The test constructs a sandbox object directly rather than starting a real containerd task. It exercises the store lookup and status conversion path in `Controller.Status`.

## State and Persistence Behavior

Only the in-memory `Store` is mutated. No containerd metadata, leases, snapshots, or files are involved.

## Dependencies and Integration Points

The fixture depends on CRI config, the OS interface, the podsandbox `types` package, and sandbox store status constants.

## Risks and Test Signals

The signal is narrow but useful: status calls work for cached sandboxes. It does not cover verbose status, not-found errors, task inspection, or plugin initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/events.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/events.go

## Purpose

This file implements the pod sandbox event handler used by the controller's event monitor. It handles task exit events for sandbox pause containers and delegates cleanup/status mutation to the shared task-exit helper.

## Important APIs, Types, and Functions

`handleEventTimeout` bounds per-event handling to ten seconds because the event monitor handles events serially. `podSandboxEventHandler` holds a controller pointer. `HandleEvent` recognizes `*eventtypes.TaskExit`, finds the sandbox by `TaskExit.ID`, skips absent or containerless entries, creates a namespaced timeout context, and calls `handleSandboxTaskExit`.

## Control Flow

Non-`TaskExit` events return nil. For task exits, the handler uses `ID` rather than `ContainerID` to avoid handling exec-process exits, then either ignores unrelated events or performs bounded cleanup.

## State and Persistence Behavior

The handler itself persists nothing. It can indirectly delete the containerd task and update the in-memory pod sandbox status through `handleSandboxTaskExit`.

## Dependencies and Integration Points

It integrates with containerd event types, the CRI namespaced context helper, the controller store, and the controller-level event monitor backoff mechanism.

## Risks and Test Signals

Risks are event loss when the sandbox is absent from the in-memory store and repeated backoff if task deletion keeps timing out. Tests are indirect through controller exit/recovery tests and event monitor behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers.go

## Purpose

This shared helper file defines constants, type registrations, root directory helpers, OCI spec generation, and metadata extraction used throughout the pod sandbox controller.

## Important APIs, Types, and Functions

Constants include `sandboxesDir`, `MetadataKey`, `UpdatedResourcesKey`, and `unknownExitCode`. `UpdatedResources` carries Linux resource and overhead updates stored as sandbox extensions. `getSandboxRootDir` and `getVolatileSandboxRootDir` map sandbox IDs under CRI root/state directories. `runtimeSpec` runs `oci.GenerateSpec` in the Kubernetes namespace. `getMetadata` extracts and type-checks CRI sandbox metadata from container extensions.

## Control Flow

`init` registers `UpdatedResources` with typeurl. Metadata extraction loads all extensions, requires `SandboxMetadataExtension`, unmarshals it, and verifies the concrete type.

## State and Persistence Behavior

The file defines durable extension keys and derives filesystem paths but does not itself write state. The extension registrations are required for marshaling and unmarshaling persisted sandbox metadata/resources.

## Dependencies and Integration Points

It depends on containerd client/container types, CRI labels, sandbox store metadata, typeurl, and the OCI spec generation package.

## Risks and Test Signals

Missing or malformed metadata extensions break recovery and status. Path helpers assume stable root/state config. Tests cover metadata typeurl round-trip and spec generation paths in adjacent files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux.go

## Purpose

This Linux helper file owns Linux-specific sandbox filesystem paths, SELinux label construction, user namespace mapping, cgroup path formatting, recursive mount cleanup, and snapshot remapping options.

## Important APIs, Types, and Functions

Key functions include `getCgroupsPath`, `pinUserNamespace`, `toLabel`, `initLabelsFromOpt`, `checkSelinuxLevel`, `unmountRecursive`, `ensureRemoveAll`, `modifyProcessLabel`, `parseUsernsIDMap`, `parseUsernsIDs`, and `snapshotterRemapOpts`. Path helpers return sandbox hostname, hosts, resolv.conf, dev-shm, and pinned namespace paths.

## Control Flow

Cgroup paths use systemd `slice:prefix:name` format when the parent basename ends in `.slice`; otherwise they join parent and sandbox ID. User namespace parsing allows no mappings for node mode and exactly one UID and one GID mapping for pod mode. `ensureRemoveAll` unmounts recursively, retries races on missing children, detaches busy mountpoints, and caps retries.

## State and Persistence Behavior

The file creates and bind-mounts pinned user namespace files and removes sandbox state directories. It also generates remapper labels for snapshots when pod user namespaces are enabled.

## Dependencies and Integration Points

It integrates with Linux syscalls, `mountinfo`, containerd mount and snapshot APIs, SELinux, seccomp, CRI runtime namespace options, and runtime spec Linux ID mappings.

## Risks and Test Signals

Risks include SELinux level regex drift, single-line ID mapping limitations, mount cleanup races, and KVM SELinux label conversion failures. Tests cover cgroup path formatting, SELinux options, ID mappings through sandbox spec tests, and root-only busy mount removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux_test.go

## Purpose

This Linux test file verifies cgroup path formatting and resilient removal of directories containing mounts.

## Important APIs, Types, and Functions

`TestGetCgroupsPath` checks regular cgroup parents, systemd slice parents, trailing slashes, and root. `TestEnsureRemoveAllWithMount` bind-mounts a temporary directory into another, runs `ensureRemoveAll`, and verifies the parent disappears.

## Control Flow

The mount cleanup test skips unless running as root, starts `ensureRemoveAll` in a goroutine, and fails if cleanup takes longer than five seconds.

## State and Persistence Behavior

The test creates temporary directories and a transient bind mount. Successful cleanup removes both the mountpoint and the containing directory.

## Dependencies and Integration Points

It depends on Linux `unix.Mount`, `os.Getuid`, and the helper functions in `helpers_linux.go`.

## Risks and Test Signals

The tests catch systemd cgroup formatting regressions and mount-removal hangs. They do not cover user namespace parsing or SELinux behavior, which are handled in other tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_other.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_other.go

## Purpose

This non-Linux, non-Windows helper file supplies portable no-op/simple implementations for helpers required by the common pod sandbox controller.

## Important APIs, Types, and Functions

`ensureRemoveAll` delegates directly to `os.RemoveAll`. `modifyProcessLabel` returns nil and does not alter the OCI spec.

## Control Flow

Both functions are single-step implementations without Linux mount retry, SELinux, or KVM label logic.

## State and Persistence Behavior

Only `ensureRemoveAll` changes filesystem state by removing the requested path. No mount or label state is managed.

## Dependencies and Integration Points

The file integrates with shared controller cleanup code under the `!windows && !linux` build tag.

## Risks and Test Signals

The simplified remove path will not handle busy mounts or Linux-style namespace artifacts. Compile and platform smoke tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_selinux_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_selinux_linux_test.go

## Purpose

This Linux test file verifies SELinux option translation and validation logic used when creating sandbox OCI specs.

## Important APIs, Types, and Functions

`TestInitSelinuxOpts` exercises nil options, user, role, type, level, and combinations passed through `initLabelsFromOpt`. `TestCheckSelinuxLevel` validates accepted MLS/MCS level formats and rejects malformed strings.

## Control Flow

The tests call helpers directly and assert success or error expectations for each table entry. They rely on the helper's label assembly and regex validation before SELinux label initialization.

## State and Persistence Behavior

No sandbox state is persisted. Depending on SELinux library behavior, label allocation can occur in process state and should be released by callers in production code.

## Dependencies and Integration Points

The tests target `toLabel`, `initLabelsFromOpt`, and `checkSelinuxLevel`, which feed Linux sandbox spec generation and cleanup.

## Risks and Test Signals

The file protects against accepting invalid SELinux level strings and against dropping user-provided SELinux components. It does not exercise container runtime enforcement.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_selinux_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_test.go

## Purpose

This cross-platform test file covers generic OCI environment deduplication behavior and basic sandbox directory removal behavior.

## Important APIs, Types, and Functions

`TestEnvDeduplication` applies repeated `oci.WithEnv` options and verifies later values override earlier ones while preserving stable order. `TestEnsureRemoveAllNotExist`, `TestEnsureRemoveAllWithDir`, and `TestEnsureRemoveAllWithFile` validate that `ensureRemoveAll` tolerates missing paths and removes directories or files.

## Control Flow

The environment test constructs a runtime spec, applies options in sequence, and compares the final `Process.Env`. Removal tests call the platform-specific `ensureRemoveAll` through the common symbol.

## State and Persistence Behavior

Only temporary files and directories are created and removed. No containerd state is used.

## Dependencies and Integration Points

It depends on OCI spec options and the platform-selected `ensureRemoveAll` implementation.

## Risks and Test Signals

The tests catch regressions in env override semantics and basic cleanup behavior. They do not cover Linux mount-specific cleanup except through the Linux-only test.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_windows.go

## Purpose

This Windows helper file provides Windows-compatible implementations for shared pod sandbox cleanup and SELinux/KVM label hooks.

## Important APIs, Types, and Functions

`ensureRemoveAll` wraps `os.RemoveAll`. `modifyProcessLabel` returns nil because SELinux process label conversion is not applicable to Windows.

## Control Flow

Both functions are direct no-op/simple implementations without retries, mount unmounts, or label mutation.

## State and Persistence Behavior

Only filesystem deletion is performed. There is no namespace, mount, SELinux, or snapshot remap behavior in this file.

## Dependencies and Integration Points

It satisfies shared helper symbols for Windows builds of the pod sandbox controller.

## Risks and Test Signals

Windows cleanup behavior depends on `os.RemoveAll` semantics and open-handle behavior. Windows sandbox spec tests provide platform coverage for the broader controller path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/opts.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/opts.go

## Purpose

This file defines a containerd task delete option that emits the legacy NRI sandbox delete notification before deleting a sandbox task.

## Important APIs, Types, and Functions

`WithNRISandboxDelete` returns a `containerd.ProcessDeleteOpts` closure. It type-checks the process as a `containerd.Task`, constructs an NRI client, builds an `nri.Sandbox` with the sandbox ID, and invokes the NRI `Delete` event for the task.

## Control Flow

If the process is not a task, NRI client creation fails, no NRI client is configured, or the NRI invocation fails, the closure logs and returns nil so task deletion continues.

## State and Persistence Behavior

No local state is persisted. It can trigger external NRI plugin side effects during task deletion.

## Dependencies and Integration Points

It integrates with containerd process delete options, NRI v0.1 APIs, task deletion in start cleanup and exit handling, and controller shutdown.

## Risks and Test Signals

The hook intentionally suppresses NRI errors, which protects cleanup but can hide plugin notification failures. Lifecycle tests that delete sandbox tasks are the main integration signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/recover.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/recover.go

## Purpose

This file lets the pod sandbox controller reconstruct in-memory sandbox state from existing containerd containers and sandbox-store extensions during CRI plugin restart.

## Important APIs, Types, and Functions

`RecoverContainer` loads sandbox metadata, container creation time, updated resources extension, task status, runtime options, and network namespace. `getNetNS` loads a non-host network namespace from metadata. `hostNetwork` contains OS-specific host-network detection for Linux, Windows HostProcess, and Darwin.

## Control Flow

Recovery uses a ten-second timeout per sandbox. It loads metadata and container info, optionally reads `UpdatedResources`, inspects the task, marks missing or stopped tasks not-ready, waits on running tasks, deletes stopped tasks, saves a `PodSandbox` in the controller store, starts an exit waiter when needed, and returns a CRI sandbox store object.

## State and Persistence Behavior

It rebuilds in-memory controller and CRI sandbox stores from persisted container extensions and sandbox-store data. It does not create new containerd resources, but it can delete stopped tasks.

## Dependencies and Integration Points

It depends on containerd container/task APIs, sandbox store metadata/status, CRI config mode, runtime API resources, netns loading, and the controller store.

## Risks and Test Signals

Risks include stale metadata, races where a task disappears during status inspection, and nil metadata assumptions after extension load. Recovery tests use fake containers/tasks to cover running, stopped, missing, and metadata cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/recover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/recover_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/recover_test.go

## Purpose

This test file validates pod sandbox recovery behavior with fake containerd container and task implementations.

## Important APIs, Types, and Functions

`fakeTask` implements the containerd task interface methods needed by recovery, including `Status`, `Wait`, `Pid`, and `Delete`. `fakeContainer` implements metadata, runtime info, task lookup, and extension access. `sandboxExtension` creates typed sandbox metadata extensions. `TestRecoverContainer` drives the controller recovery path through table cases.

## Control Flow

The test builds fake containers with different metadata/task/status combinations, calls `RecoverContainer`, and asserts recovered sandbox status, store contents, and error handling. Fakes return not-found and status values to simulate restart races.

## State and Persistence Behavior

The fake controller store is mutated by recovery. No real containerd, filesystem, or namespace state is used.

## Dependencies and Integration Points

It exercises typeurl metadata decoding, sandbox status reconstruction, task wait channel registration, and controller store save behavior.

## Risks and Test Signals

The tests catch regressions in restart reconstruction and not-found handling. They cannot validate real shim/task-service cleanup, netns filesystem state, or concurrent task deletion timing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/recover_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_delete.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_delete.go

## Purpose

This file implements sandbox controller shutdown and low-level pause task/container cleanup.

## Important APIs, Types, and Functions

`Shutdown` removes sandbox root and volatile directories, deletes the sandbox task if present, deletes the container with snapshot cleanup, and removes the sandbox from the controller store. `cleanupSandboxTask` deletes the task and, when shim/task caches diverge, calls the task service `Delete` API to ensure the shim is shut down.

## Control Flow

Missing sandbox IDs are treated as successful no-ops. Cleanup removes filesystem state before container deletion. Task deletion tolerates not-found, then performs task-service cleanup to handle leaked shims after canceled or partially completed shim deletes.

## State and Persistence Behavior

It deletes root/state directories, containerd task state, snapshots, container metadata, and in-memory store entries.

## Dependencies and Integration Points

It integrates with `ensureRemoveAll`, containerd container/task APIs, the tasks service gRPC API, errdefs conversion, and NRI delete hooks in other delete paths.

## Risks and Test Signals

Risks include leaving shims when task-service cleanup fails and losing diagnostic state after directory removal. End-to-end remove and restart tests are needed because this file touches real runtime cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run.go

## Purpose

This file implements the pod sandbox controller's create/start path for pause-container-backed sandboxes.

## Important APIs, Types, and Functions

`CleanupErr` marks cleanup failures joined with startup errors. `Start` creates root directories, loads the pause image, resolves sandbox runtime, builds the OCI spec, creates a container and task, sets up files, invokes deprecated NRI create hooks, starts the task, updates status, returns `sandbox.ControllerInstance`, and starts an exit waiter. `Create` stores metadata from sandbox extensions. `getSandboxImageName` selects the pinned sandbox image or default.

## Control Flow

`Start` is a staged resource acquisition function with defers for rollback. Each cleanup defer runs only on later error and joins cleanup failures separately. It records SELinux labels, handles privileged sysfs changes, chooses runtime snapshotter, marshals the final task spec, and starts a background wait goroutine after task start.

## State and Persistence Behavior

It creates sandbox filesystem directories, containerd snapshots/containers/tasks, metadata extensions, runtime labels, and in-memory status. On failure it attempts to unwind directories, files, tasks, containers, labels, and snapshots.

## Dependencies and Integration Points

It integrates with CRI config, image service config, containerd client APIs, OCI spec options, snapshot labels, NRI, SELinux, warning/deprecation service, and the controller store.

## Risks and Test Signals

Risks include partial cleanup, deprecated NRI behavior, SELinux label leaks, and cleanup order dependencies. Tests cover spec generation and metadata typeurl; full safety needs runtime integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux.go

## Purpose

This Linux file builds the sandbox OCI spec and required sandbox files for Linux pause containers.

## Important APIs, Types, and Functions

`sandboxContainerSpec` configures rootfs, env, args, hostname, cgroups, namespaces, user namespaces, `/dev/shm`, `/etc/resolv.conf`, SELinux, sysctls, OOM score, resources, and CRI annotations. `sandboxContainerSpecOpts` handles seccomp and user selection. `setupSandboxFiles` writes hostname, hosts, resolv.conf, and mounts tmpfs shm. `parseDNSOptions`, `cleanupSandboxFiles`, and `sandboxSnapshotterOpts` support those paths.

## Control Flow

Spec generation rejects images with no entrypoint or command, removes namespaces requested as host/node, pins user namespaces when pod userns combines with non-host network, creates bind mounts for shm and DNS, adjusts sysctls for unprivileged ports/ICMP, and returns a generated OCI spec. File setup writes files before mounting shm, while cleanup unmounts shm unless host IPC is used.

## State and Persistence Behavior

It writes sandbox files under root dir, mounts tmpfs under volatile state, creates pinned namespace bind mounts, and emits snapshot remap labels for user namespaces.

## Dependencies and Integration Points

It integrates with OCI spec options, CRI namespace/security config, SELinux, seccomp profile utilities, userns detection, syscalls, annotations, and snapshotter options.

## Risks and Test Signals

Risks include invalid user namespace mappings, sysctl mutation of config maps, mount cleanup failures, and SELinux label leaks. Linux spec/file tests cover namespace, DNS, annotations, seccomp, user, host IPC/network, and file setup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux_test.go

## Purpose

This large Linux test file validates sandbox OCI spec generation, sandbox file setup, and DNS option rendering for Linux pod sandboxes.

## Important APIs, Types, and Functions

`getRunPodSandboxTestData` creates default CRI sandbox config, image config, and spec assertions. `TestLinuxSandboxContainerSpec` covers entrypoint/cmd validation, namespace modes, host cgroups, SELinux, seccomp, sysctls, user/group handling, passthrough annotations, resources, user namespaces, and privileged behavior. `TestSetupSandboxFiles` checks hostname, hosts, resolv.conf, and shm setup. `TestParseDNSOption` checks resolv.conf formatting.

## Control Flow

Tests mutate default config/image data per case, call `sandboxContainerSpec` or setup helpers, and assert concrete OCI spec fields or files. Some root-sensitive paths skip when privileges are unavailable.

## State and Persistence Behavior

Temporary sandbox roots are written and, for shm cases, mounted and cleaned up. No real containerd tasks are started.

## Dependencies and Integration Points

The tests exercise Linux helpers, CRI config defaults, OCI generation, security profile utilities, and OS abstraction behavior.

## Risks and Test Signals

This is the main regression signal for Linux sandbox spec compatibility. It does not replace full runtime tests because kernel, runtime, and CNI behavior are mostly mocked or skipped.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other.go

## Purpose

This non-Linux, non-Windows file supplies minimal sandbox spec and file hooks for other platforms.

## Important APIs, Types, and Functions

`sandboxContainerSpec` returns a generated runtime spec with default CRI annotations only. `sandboxContainerSpecOpts`, `setupSandboxFiles`, `cleanupSandboxFiles`, and `sandboxSnapshotterOpts` return empty options or nil.

## Control Flow

All functions are straight-line stubs. Spec generation ignores image config, namespace path, and runtime pod annotation inputs except for CRI default annotations.

## State and Persistence Behavior

No sandbox files, mounts, or snapshotter remap state are created by this file.

## Dependencies and Integration Points

It exists under `!windows && !linux` to satisfy the shared controller start path on other platforms.

## Risks and Test Signals

The behavior is intentionally minimal and may not create a runnable pause container on every platform. Compile and platform-specific smoke tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other_test.go

## Purpose

This non-Linux, non-Windows test helper supplies platform-specific default data for shared sandbox spec tests.

## Important APIs, Types, and Functions

`getRunPodSandboxTestData` returns empty `PodSandboxConfig`, empty image config, and a no-op spec check closure.

## Control Flow

There are no test cases in this file; it satisfies symbols consumed by shared tests compiled on other platforms.

## State and Persistence Behavior

No state is created or persisted.

## Dependencies and Integration Points

It integrates with `sandbox_run_test.go` under the `!windows && !linux` build tag.

## Risks and Test Signals

Because assertions are empty, shared tests provide only compile-level coverage for these platforms. Platform-specific behavior needs dedicated tests if support expands.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_test.go

## Purpose

This shared test file validates platform-neutral sandbox spec behavior and typeurl metadata round-tripping.

## Important APIs, Types, and Functions

`TestEmpty` registers the root-required flag for all platforms. `TestSandboxContainerSpec` checks empty entrypoint/cmd errors and OCI passthrough annotation filtering, including wildcard matching. `TestTypeurlMarshalUnmarshalSandboxMeta` verifies `sandboxstore.Metadata` can be marshaled and unmarshaled through typeurl with original and Linux-enriched configs.

## Control Flow

The spec test obtains platform-specific baseline config from `getRunPodSandboxTestData`, applies case mutations, calls `sandboxContainerSpec`, then runs shared and case-specific assertions.

## State and Persistence Behavior

No real sandbox state is created. Metadata serialization exercises in-memory protobuf/typeurl representation that is also used for persisted container extensions.

## Dependencies and Integration Points

It integrates with platform-specific test helper files, CRI annotations, sandbox metadata, and typeurl registration.

## Risks and Test Signals

The tests catch annotation pass-through and metadata compatibility regressions. They skip some unsupported OSes and do not start real tasks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows.go

## Purpose

This Windows file builds the sandbox OCI spec for Windows pause containers and supplies Windows no-op file/snapshot hooks.

## Important APIs, Types, and Functions

`sandboxContainerSpec` sets image env, hostname, cwd, process args, clears root, sets the HCS network namespace, applies default sandbox CPU shares, chooses RunAs username, applies credential spec, forwards allowed annotations, records HostProcess annotation, and adds default CRI annotations. Other hooks return nil or empty options.

## Control Flow

Spec generation rejects images with no entrypoint or command. CRI `RunAsUsername` overrides image user. Credential spec is added only when present. File setup and cleanup are no-ops because Windows does not need the Linux sandbox files.

## State and Persistence Behavior

No files or mounts are created. State is limited to generated OCI spec fields and annotations.

## Dependencies and Integration Points

It integrates with hcsshim-facing Windows OCI fields, CRI Windows security context, default CRI annotations, and shared controller start logic.

## Risks and Test Signals

Risks include user validation being deferred to hcsshim and incomplete HostProcess/network namespace combinations. Windows tests assert network namespace, user override, credential spec, CPU shares, and annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows_test.go

## Purpose

This Windows test file provides Windows sandbox spec fixtures and validates network namespace placement in the generated OCI spec.

## Important APIs, Types, and Functions

`getRunPodSandboxTestData` returns a Windows sandbox config with metadata, hostname, labels, annotations, RunAs username, credential spec, and HostProcess flag, plus image config and a spec assertion closure. `TestSandboxWindowsNetworkNamespace` checks that `spec.Windows.Network.NetworkNamespace` equals the provided namespace path.

## Control Flow

The test builds a controller fixture, generates a spec with `sandboxContainerSpec`, runs the shared spec checks, and asserts Windows network fields are present.

## State and Persistence Behavior

No containerd or filesystem state is created.

## Dependencies and Integration Points

It exercises Windows-specific spec options, CRI annotations, and the shared controller test fixture.

## Risks and Test Signals

The test catches Windows spec regressions but not real HCS runtime behavior or HostProcess networking semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stats.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stats.go

## Purpose

This controller file reserves a metrics API for sandbox controllers but currently marks it unimplemented.

## Important APIs, Types, and Functions

`(*Controller).Metrics` accepts a sandbox ID and returns `nil, errdefs.ErrNotImplemented`.

## Control Flow

The method is a direct stub. It does not inspect the controller store or containerd metrics.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies part of the sandbox controller surface and returns containerd API `types.Metric` when implemented in the future.

## Risks and Test Signals

Callers must not assume controller-level metrics are available. Compile coverage and CRI stats tests for the outer service are the current signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_status.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_status.go

## Purpose

This file implements controller-level sandbox status and verbose CRI sandbox info construction.

## Important APIs, Types, and Functions

`Status` returns `sandbox.ControllerStatus` from the in-memory `PodSandbox` status. `toCRISandboxInfo` builds a JSON-encoded `types.SandboxInfo` map including PID, config, CNI result, task status, runtime spec, image, snapshot metadata, runtime options, and network namespace closed state. `getRuntimeOptions` unpacks runtime options from container metadata.

## Control Flow

Status lookup fails with not-found when the sandbox is absent. Verbose info optionally loads task status, spec, container info, and runtime options, tolerating task not-found as deleted status but propagating other errors.

## State and Persistence Behavior

The file reads in-memory sandbox status and containerd metadata/spec/task state. It does not mutate state.

## Dependencies and Integration Points

It integrates with containerd container/task APIs, typeurl runtime options, netns status checks, and CRI verbose `info` JSON expected by kubelet clients.

## Risks and Test Signals

Verbose status can fail if container spec/info retrieval fails or netns closed checks error. Tests cover basic non-verbose status; verbose behavior needs integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stop.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stop.go

## Purpose

This file stops a running sandbox pause container and cleans sandbox files while preserving exit-event driven task deletion semantics.

## Important APIs, Types, and Functions

`Stop` finds the cached sandbox, loads metadata, stops ready or unknown sandboxes, and calls platform cleanup. `stopSandboxContainerRetryOnConnectionClosed` retries shim ttrpc closed errors with quadratic backoff. `stopSandboxContainer` kills the task and waits for sandbox exit. `cleanupUnknownSandbox` reuses task-exit cleanup with an unknown exit code.

## Control Flow

Missing store entries return not-found; a nil container is already stopped. Unknown state starts a temporary exit monitor before killing so cleanup/status update still happen. Task not-found is tolerated except in unknown state, where cleanup is forced.

## State and Persistence Behavior

The method can send SIGKILL, wait for status to become not-ready, and unmount/remove platform sandbox files. Status mutation occurs through `waitSandboxExit` or `cleanupUnknownSandbox`.

## Dependencies and Integration Points

It integrates with containerd task APIs, errdefs, shim ttrpc error detection, Linux cleanup helpers, and the shared task-exit handler.

## Risks and Test Signals

Risks include indefinite waits if task exit is not observed, retry masking persistent shim failures, and cleanup races in unknown state. Integration stop/remove tests are needed for confidence.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/store.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/store.go

## Purpose

This file defines the in-memory store used by the pod sandbox controller for live `PodSandbox` objects.

## Important APIs, Types, and Functions

`Store` wraps `sync.Map`. `NewStore` allocates it. `Save` rejects nil sandboxes and stores by ID. `Get` loads and type-asserts a sandbox. `Remove` atomically deletes and returns the previous sandbox.

## Control Flow

All operations are direct map wrappers with nil/not-found handling.

## State and Persistence Behavior

State is process-local and lost on restart. Recovery repopulates it from containerd metadata.

## Dependencies and Integration Points

It stores `server/podsandbox/types.PodSandbox` values for controller start, stop, status, wait, event, and recovery flows.

## Risks and Test Signals

The store does not prevent duplicate saves or validate IDs beyond nil object checks. Controller and recovery tests indirectly validate its behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox.go

## Purpose

This file defines the live pod sandbox object used by the controller, including wait/exit synchronization and mutable status storage.

## Important APIs, Types, and Functions

`PodSandbox` carries ID, containerd container, metadata, runtime options, status storage, and a stop channel. `NewPodSandbox` initializes status and immediately stops the wait channel for not-ready sandboxes. `Exit` updates state to not-ready, records exit status/time, clears PID, and stops waiters. `Wait` blocks until context cancellation or exit.

## Control Flow

`Wait` selects on context or the stop channel. `Exit` performs an atomic status update before signaling waiters.

## State and Persistence Behavior

Status is in-memory through `sandboxstore.StatusStorage`. Exit state can be reconstructed on recovery, but the stop channel is process-local.

## Dependencies and Integration Points

It integrates with containerd exit status values, sandbox runtime options, CRI sandbox metadata, and the generic store stop channel.

## Risks and Test Signals

Risks include callers waiting forever if `Exit` is never called and loss of wait channel state across restart. The unit test validates status mutation, wait timeout, and exit wakeup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox_test.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox_test.go

## Purpose

This unit test validates `PodSandbox` lifecycle status and wait/exit synchronization.

## Important APIs, Types, and Functions

`Test_PodSandbox` creates a sandbox, updates it to ready with PID and creation time, starts one waiter expected to time out and one waiter expected to receive exit status, then calls `Exit`.

## Control Flow

The test uses a wait group with two goroutines. One context times out before exit; the other waits until `Exit` closes the stop channel and returns code 128 with the expected exit time.

## State and Persistence Behavior

Only in-memory status and stop channel state are exercised.

## Dependencies and Integration Points

It depends on sandbox store status types and containerd exit status conversion.

## Risks and Test Signals

The test catches regressions in wait cancellation and exit signaling. It does not cover repeated `Exit` calls or concurrent status updates beyond this simple case.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/types/sandbox_info.go -->
# sources/cloud-native/containerd/internal/cri/server/podsandbox/types/sandbox_info.go

## Purpose

This file defines the JSON payload shape used for verbose pod sandbox status information.

## Important APIs, Types, and Functions

`SandboxInfo` includes PID, process status, netns closed flag, image, snapshot key/snapshotter, runtime type/options, original CRI config, runtime spec, CNI result, sandbox metadata, and optional overhead/resources.

## Control Flow

There are no functions or control flow.

## State and Persistence Behavior

The struct is serialized into the `info` map returned by sandbox status. It represents observed state but does not persist it directly.

## Dependencies and Integration Points

It depends on CNI result types, OCI runtime spec, CRI runtime API types, and sandbox store metadata.

## Risks and Test Signals

Because `RuntimeOptions` is `any`, JSON shape can vary by runtime option type. Verbose status clients should tolerate absent fields such as `RuntimeSpec` for partially created sandboxes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/podsandbox/types/sandbox_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/rdt.go -->
# sources/cloud-native/containerd/internal/cri/server/rdt.go

## Purpose

This file implements RDT class selection from container and pod annotations when the build includes RDT support.

## Important APIs, Types, and Functions

`(*criService).rdtClassFromAnnotations` calls `rdt.ContainerClassFromAnnotations`, verifies that RDT is enabled before returning a non-empty class, optionally ignores not-enabled errors based on config, and otherwise returns the selected class.

## Control Flow

Annotation parsing happens first. If a class is requested while RDT is disabled, an error is produced unless `IgnoreRdtNotEnabledErrors` is set and RDT is not enabled.

## State and Persistence Behavior

No state is persisted. The returned class is consumed by container creation resource/runtime configuration elsewhere.

## Dependencies and Integration Points

It integrates with `pkg/rdt`, CRI service config, and container creation paths that apply RDT classes.

## Risks and Test Signals

Risks include silently ignoring RDT requests when the ignore flag is enabled and rejecting container creation when host support is absent. Tests should cover annotation precedence and disabled-host behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/rdt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/rdt_stub.go -->
# sources/cloud-native/containerd/internal/cri/server/rdt_stub.go

## Purpose

This `no_rdt` build-tag file disables RDT class selection while preserving the CRI service method set.

## Important APIs, Types, and Functions

`(*criService).rdtClassFromAnnotations` ignores all inputs and returns an empty class with nil error.

## Control Flow

The method is a direct no-op.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It integrates through build tags with container creation code that always calls the method regardless of RDT build support.

## Risks and Test Signals

The risk is silent loss of requested RDT annotations in `no_rdt` builds. Compile tests and build-tag-specific container creation tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/rdt_stub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/restart.go -->
# sources/cloud-native/containerd/internal/cri/server/restart.go

## Purpose

This file reconstructs CRI service state after containerd/CRI plugin restart, loading sandboxes, containers, images, IO, name indexes, exit monitors, and orphaned directories.

## Important APIs, Types, and Functions

`recover` loads old pause-container sandboxes, new sandbox-store records, running wait monitors, containers, and images. `loadContainer` reconstructs container metadata, status, IO, task state, and wait channels. `podSandboxRecover` is the controller recovery interface. `getNetNS`, `cleanupOrphanedIDDirs`, and `createContainerIO` support recovery.

## Control Flow

Recovery lists sandbox containers, delegates each to the podsandbox controller, then reconciles sandbox-store records not already loaded. It starts wait monitors for ready sandboxes, loads containers in parallel, validates task/checkpoint consistency, checks images, and removes orphaned root/state directories. Per-container loads are capped by a ten-second timeout.

## State and Persistence Behavior

It repopulates in-memory sandbox/container stores and name indexes from containerd metadata and status checkpoints. It may delete created/stopped tasks, update unknown container status, attach IO, and remove orphaned directories.

## Dependencies and Integration Points

It integrates with containerd container APIs, sandbox service, podsandbox recovery, CRI store/checkpoint types, image service, netns, typeurl metadata, errgroup concurrency, and filesystem cleanup.

## Risks and Test Signals

Risks include stale checkpoints, races with task deletion, leaked shims, missing metadata extensions, and accidental cleanup of directories for externally modified containers. Recovery tests and restart integration tests are essential.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/restart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config.go -->
# sources/cloud-native/containerd/internal/cri/server/runtime_config.go

## Purpose

This file implements the CRI `RuntimeConfig` RPC wrapper.

## Important APIs, Types, and Functions

`(*criService).RuntimeConfig` returns a `runtime.RuntimeConfigResponse` whose `Linux` field is supplied by the platform-specific `getLinuxRuntimeConfig`.

## Control Flow

The function allocates the response and delegates all platform logic. It ignores the request fields because the CRI request has no options used here.

## State and Persistence Behavior

No state is mutated. It reads service configuration indirectly through the platform helper.

## Dependencies and Integration Points

It integrates with kubelet's CRI runtime config query and Linux/non-Linux build-tag implementations.

## Risks and Test Signals

The wrapper is simple; meaningful risk lies in platform helper accuracy. Linux tests call this API to verify cgroup driver selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/runtime_config_linux.go

## Purpose

This Linux file reports the effective cgroup driver to CRI clients.

## Important APIs, Types, and Functions

`getLinuxRuntimeConfig` returns `LinuxRuntimeConfiguration` with `CgroupDriver`. `getCgroupDriver` inspects configured runtimes in deterministic order, preferring the default runtime, then sorted names. `getCgroupDriverFromRuntimeHandlerOpts` recognizes runc options and maps `SystemdCgroup` to CRI cgroup driver enum.

## Control Flow

The service tries to generate runtime options per handler. The first handler that exposes runc cgroup settings wins. If none do, it auto-detects systemd and returns systemd or cgroupfs accordingly.

## State and Persistence Behavior

No state is persisted. It reads runtime configuration and host systemd state.

## Dependencies and Integration Points

It integrates with CRI runtime config, containerd runtime option generation, runc options, and systemd detection.

## Risks and Test Signals

Risks include returning default systemd for unrecognized option types and picking a non-obvious runtime when the default is absent. Tests cover no runtime, non-runc, alphabetical fallback, and default runtime preference.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/runtime_config_linux_test.go

## Purpose

This Linux test file validates CRI runtime config cgroup driver selection.

## Important APIs, Types, and Functions

`newFakeRuntimeConfig` builds fake runtimes with optional runc v2 and `SystemdCgroup`. `TestRuntimeConfig` asserts the response for no runtimes, non-runc runtimes, sorted fallback, and default runtime priority.

## Control Flow

Each test mutates a test CRI service config, calls `RuntimeConfig`, and compares `resp.Linux.CgroupDriver` to expected values, using host systemd detection only for fallback cases.

## State and Persistence Behavior

Only in-memory test configuration is changed.

## Dependencies and Integration Points

It exercises `RuntimeConfig`, `getCgroupDriver`, runtime option generation, and systemd auto-detection.

## Risks and Test Signals

The test protects kubelet-visible cgroup driver reporting. It does not cover malformed runtime options beyond the helper's normal generation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config_other.go -->
# sources/cloud-native/containerd/internal/cri/server/runtime_config_other.go

## Purpose

This non-Linux file disables Linux runtime configuration reporting on other platforms.

## Important APIs, Types, and Functions

`getLinuxRuntimeConfig` returns nil.

## Control Flow

The method is a direct stub.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform helper used by `RuntimeConfig` under `!linux`.

## Risks and Test Signals

Non-Linux clients receive no Linux runtime config, which matches the platform. Compile and platform CRI smoke tests are sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/runtime_config_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_list.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_list.go

## Purpose

This file implements CRI pod sandbox listing and filtering from the in-memory sandbox store.

## Important APIs, Types, and Functions

`ListPodSandbox` converts all stored sandboxes to CRI `PodSandbox` objects and applies filters. `toCRISandbox` maps metadata/status to CRI state and fields. `normalizePodSandboxFilter` and `normalizePodSandboxStatsFilter` expand truncated IDs through the store. `filterCRISandboxes` applies ID, state, and label selectors.

## Control Flow

Listing does not query containerd. It snapshots the current store, maps ready state to `SANDBOX_READY` and all other states to `SANDBOX_NOTREADY`, normalizes IDs, and filters sequentially.

## State and Persistence Behavior

No state is mutated except the request filter ID may be normalized in place.

## Dependencies and Integration Points

It integrates with CRI runtime API, sandbox store, metrics timers, and stats filtering helpers.

## Risks and Test Signals

Risks include in-place filter mutation and not distinguishing unknown from not-ready in CRI output. Tests cover conversion, truncated IDs, state filters, label filters, and mixed filters.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_list_test.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_list_test.go

## Purpose

This test file validates CRI sandbox conversion and filtering behavior.

## Important APIs, Types, and Functions

`TestToCRISandbox` checks metadata, labels, annotations, runtime handler, created time, and state mapping. `TestFilterSandboxes` populates a test sandbox store and verifies no filter, full ID, truncated ID, state, label, and mixed filter cases.

## Control Flow

Tests build sandbox store objects, convert them to CRI objects, insert them into the service store for ID normalization, and compare filtered slices.

## State and Persistence Behavior

Only the in-memory test sandbox store is mutated.

## Dependencies and Integration Points

It exercises `toCRISandbox`, `filterCRISandboxes`, and store-based truncated ID normalization.

## Risks and Test Signals

The tests catch user-visible list filtering regressions. They do not test concurrent store mutation or stats filter normalization separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward.go

## Purpose

This file implements the CRI `PortForward` RPC entrypoint that returns a streaming endpoint for a ready pod sandbox.

## Important APIs, Types, and Functions

`PortForward` looks up the sandbox by requested ID, verifies it is ready, and delegates endpoint creation to `streamServer.GetPortForward`.

## Control Flow

The method fails if the sandbox cannot be found or is not ready. It does not validate requested ports against pod declarations.

## State and Persistence Behavior

No state is mutated. It reads the sandbox store and allocates a streaming server response.

## Dependencies and Integration Points

It integrates with CRI streaming server setup and platform-specific `portForward` implementations that execute the actual byte forwarding.

## Risks and Test Signals

Risks include allowing undeclared ports and stale ready state. Streaming integration tests are needed for full coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_linux.go

## Purpose

This Linux file performs the actual port-forward data path by entering a sandbox network namespace and proxying bytes to localhost inside that namespace.

## Important APIs, Types, and Functions

`portForward` loads the sandbox, chooses either the sandbox netns or host namespace, dials `localhost:<port>` inside the namespace, and copies bytes in both directions between the stream and TCP connection.

## Control Flow

For non-host networking it checks the netns is not closed and uses `NetNS.Do`; host networking runs directly. It dials IPv4 first, then IPv6 to avoid Go Happy Eyeballs running outside the namespace. It waits for one copy direction to finish, then gives the other one second to close or responds to context cancellation.

## State and Persistence Behavior

No persistent state is changed. The stream is closed after namespace execution, and TCP connections are closed with defers.

## Dependencies and Integration Points

It integrates with CNI netns objects, Go networking, CRI streaming server callbacks, and sandbox store network state.

## Risks and Test Signals

Risks include hangs on half-closed streams, failed dual-stack fallback, and closed netns races. Integration tests with real netns and stream cancellation are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_other.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_other.go

## Purpose

This non-Linux, non-Windows file marks port forwarding unsupported.

## Important APIs, Types, and Functions

`portForward` returns `port forward: ErrNotImplemented`.

## Control Flow

The function is a direct error return.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform-specific port-forward symbol under `!windows && !linux`.

## Risks and Test Signals

Callers must surface the not-implemented error cleanly. Build-tag compile tests are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_windows.go

## Purpose

This Windows file implements port forwarding by dialing the pod IP or localhost and proxying bytes between the CRI stream and TCP connection.

## Important APIs, Types, and Functions

`portForward` loads the sandbox, resolves the pod IP with `getIPs` for non-host networking or uses `localhost` for HostProcess/host networking, dials the requested port, and starts bidirectional `io.Copy` goroutines.

## Control Flow

The function waits for the first copy direction or context cancellation, then waits up to one second for the second direction. Errors are wrapped with pod ID and pod IP context.

## State and Persistence Behavior

No persistent state is changed. Network connections are closed by defers.

## Dependencies and Integration Points

It integrates with Windows CRI networking state, sandbox store IP lookup helpers, streaming server callbacks, and Go TCP networking.

## Risks and Test Signals

Risks include stale pod IPs and stream half-close timing. Windows networking integration tests are needed beyond compile coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_remove.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_remove.go

## Purpose

This file implements CRI `RemovePodSandbox`, force-stopping a sandbox, removing contained containers, deleting sandbox controller state, notifying NRI, and releasing indexes.

## Important APIs, Types, and Functions

`RemovePodSandbox` resolves the sandbox, calls `stopPodSandbox`, deletes the lease, checks netns closure, removes all containers in the sandbox, calls `sandboxService.ShutdownSandbox`, sends a deleted event, invokes `nri.RemovePodSandbox`, deletes in-memory and containerd sandbox-store metadata, releases the sandbox name, and updates metrics.

## Control Flow

Missing sandboxes are successful no-ops. Removal blocks NRI plugin sync during critical operations. It force-stops before removing containers and refuses to continue if a non-host netns is still open.

## State and Persistence Behavior

It deletes leases, network state through stop logic, containers, sandbox controller resources, CRI stores, containerd sandbox-store records, and name reservations.

## Dependencies and Integration Points

It integrates with leases, sandbox service, container removal, NRI, event generation, tracing, and metrics.

## Risks and Test Signals

Risks include container creation races after the stop point, netns closure failures, and partial metadata cleanup. End-to-end CRI remove tests and restart recovery are key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_run.go

## Purpose

This file implements CRI `RunPodSandbox`, including ID/name reservation, lease creation, sandbox metadata persistence, network namespace and CNI setup, sandbox controller creation/start, NRI notification, store insertion, events, and helper conversion functions.

## Important APIs, Types, and Functions

`RunPodSandbox` is the main CRI entrypoint. Helpers include `ensurePauseImageExists`, `getNetworkPlugin`, `setupPodNetwork`, `cniNamespaceOpts`, `toCNILabels`, `toCNIBandWidth`, `toCNIPortMappings`, `toCNIDNS`, `selectPodIPs`, `ipString`, and `logDebugCNIResult`.

## Control Flow

The run path generates an ID, reserves the sandbox name, creates a lease, resolves runtime/sandboxer, stores metadata extension, creates and configures a network namespace when not host networking, runs CNI setup, creates the sandbox through the sandbox service, ensures the pause image unless disabled, starts the sandbox, stores returned labels/spec, runs NRI, marks ready, inserts into the store, sends created/started events, starts an exit monitor, and rolls back on errors.

## State and Persistence Behavior

It creates leases, sandbox-store records, netns mounts, CNI allocations, controller resources, in-memory sandbox store entries, labels/spec, process labels, and event records. Defers clean up name reservations, leases, metadata, CNI, netns, and started sandboxes on failure.

## Dependencies and Integration Points

It integrates with CRI config, sandbox service/controllers, containerd leases and sandbox store, CNI, NRI, tracing, metrics, image service, and CRI events.

## Risks and Test Signals

Risks include complex rollback ordering, user namespace netns setup, CNI partial failures, and pause image policy. Tests cover CNI conversion, IP selection, and disable-pause-image-pull config; integration tests cover the full path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_run_linux.go

## Purpose

This Linux file provides CRI service helpers for loopback setup and network namespace creation inside a pod user namespace.

## Important APIs, Types, and Functions

`bringUpLoopback` enters a netns and sets link `lo` up. `setupNetnsWithinUserns` validates pod user namespace settings and uses `sys.UnshareAfterEnterUserns` with UID/GID maps and `CLONE_NEWNET` to create a network namespace whose mount is captured by `netns.NewNetNSFromPID`.

## Control Flow

User namespace netns setup requires pod mode, exactly one non-nil UID mapping, and exactly one non-nil GID mapping. It formats mapping strings, unshares network after entering userns, mounts the new netns from the child PID, and returns it.

## State and Persistence Behavior

It can create and mount a network namespace under the requested mount directory and change loopback state inside a netns.

## Dependencies and Integration Points

It integrates with CNI setup, CRI user namespace options, containerd netns helpers, Linux netlink, and containerd sys userns helpers.

## Risks and Test Signals

Risks include invalid mappings, kernel permission failures, and netns mount leaks. This behavior needs root/integration tests on Linux userns-capable kernels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_other.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_run_other.go

## Purpose

This non-Linux, non-Windows file supplies CRI service sandbox network helper stubs for other Unix-like platforms.

## Important APIs, Types, and Functions

`bringUpLoopback` returns nil. `setupNetnsWithinUserns` returns an unsupported error for setting up netns within userns.

## Control Flow

Both functions are direct returns.

## State and Persistence Behavior

No network namespace or link state is changed.

## Dependencies and Integration Points

It satisfies symbols used by `RunPodSandbox` under `!windows && !linux`.

## Risks and Test Signals

Pod user namespaces with sandbox networking are unsupported on these platforms. Compile and platform smoke tests are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_test.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_run_test.go

## Purpose

This CRI service test file validates helper conversions used by sandbox network setup and runtime configuration selection.

## Important APIs, Types, and Functions

`TestToCNIPortMappings` verifies CRI port mappings convert to CNI mappings and host-port-less entries are skipped. `TestSelectPodIP` verifies IPv4 default, IPv6 preference, CNI order preference, and additional IP ordering. `TestDisablePauseImagePullConfig` validates runtime config plumbing for `DisablePauseImagePull`.

## Control Flow

Tests construct CRI objects or CNI IP configs, call pure helper functions, and assert exact output slices/fields.

## State and Persistence Behavior

No persistent state is used. The runtime config test mutates only an in-memory config object.

## Dependencies and Integration Points

It covers CNI option conversion helpers and CRI config runtime resolution used by `RunPodSandbox`.

## Risks and Test Signals

The tests catch common network option regressions but do not validate actual CNI plugin calls or full sandbox startup rollback.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_run_windows.go

## Purpose

This Windows CRI service file supplies platform-specific sandbox network helper behavior.

## Important APIs, Types, and Functions

`bringUpLoopback` returns nil because loopback setup is not performed here. `setupNetnsWithinUserns` returns an unsupported error for Windows.

## Control Flow

Both functions are direct returns.

## State and Persistence Behavior

No network namespace or interface state is changed.

## Dependencies and Integration Points

It satisfies `RunPodSandbox` helper symbols for Windows builds.

## Risks and Test Signals

Pod user namespace network namespace setup is unsupported on Windows. Windows sandbox run and portforward tests should cover supported network behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_run_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_service.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_service.go

## Purpose

This file defines a small CRI-facing sandbox service facade over containerd sandbox controllers.

## Important APIs, Types, and Functions

`criSandboxService` stores sandbox controllers by sandboxer name and CRI config. Methods include `SandboxController`, `CreateSandbox`, `StartSandbox`, `WaitSandbox`, `SandboxStatus`, `SandboxPlatform`, `ShutdownSandbox`, `UpdateSandbox`, and `StopSandbox`.

## Control Flow

Each operation resolves the requested sandbox controller and delegates to it. `WaitSandbox` wraps a blocking controller `Wait` call in a goroutine and returns a buffered channel containing a containerd `ExitStatus`.

## State and Persistence Behavior

The facade itself persists no sandbox state. It delegates all mutations to controllers and returns wait results through channels.

## Dependencies and Integration Points

It integrates CRI service code with the generic `core/sandbox.Controller` interface and containerd exit status type.

## Risks and Test Signals

Risks include missing sandboxer names and goroutine lifetime tied to wait context. Sandbox run/recovery tests exercise the facade indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_stats.go

## Purpose

This file implements the CRI `PodSandboxStats` RPC wrapper and common cgroup metrics container type.

## Important APIs, Types, and Functions

`PodSandboxStats` looks up a sandbox and delegates to platform-specific `podSandboxStats`, returning a `PodSandboxStatsResponse`. `cgroupMetrics` holds either cgroup v1 or v2 metrics.

## Control Flow

The RPC fails on missing sandbox or platform stats failure and wraps errors with sandbox ID context.

## State and Persistence Behavior

No state is mutated. It reads the sandbox store and platform metrics.

## Dependencies and Integration Points

It integrates with CRI stats API, sandbox store, cgroup stats packages, and platform-specific stats implementations.

## Risks and Test Signals

Risk lies mostly in platform metrics collection and ready-state assumptions. Stats integration tests on Linux are needed for full confidence.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_stats_linux.go

## Purpose

This Linux file collects pod sandbox CPU, memory, process, container, and network statistics for CRI.

## Important APIs, Types, and Functions

`podSandboxStats` validates ready state, loads cgroup metrics, builds `PodSandboxStats`, computes CPU/memory via container stats helpers, collects all non-loopback netns interface stats, lists child container stats, and sums process counts. `getContainerNetIO` and `getAllContainerNetIO` inspect netlink inside a netns. `cgroupMetricsForSandbox` loads cgroup v1 or v2 metrics from the sandbox cgroup parent.

## Control Flow

Stats collection fails if the sandbox is not ready or has no valid cgroup parent. Network stats are collected only when `NetNSPath` is set. Default interface is `eth0` when present, otherwise the first non-loopback interface.

## State and Persistence Behavior

No persistent state is changed. It reads cgroup files and netns link statistics.

## Dependencies and Integration Points

It integrates with cgroups v1/v2, netlink, CNI netns, CRI container stats helpers, and sandbox store metadata/status.

## Risks and Test Signals

Risks include missing cgroup parent, closed netns, cgroup mode differences, and interface ordering. Linux stats integration tests should cover v1/v2 and multi-interface cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_list.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_stats_list.go

## Purpose

This file implements CRI `ListPodSandboxStats` with filtering and concurrent per-sandbox stats collection.

## Important APIs, Types, and Functions

`ListPodSandboxStats` selects sandboxes, starts one goroutine per sandbox, calls `podSandboxStats`, suppresses transient unavailable/not-found/closed errors, joins hard errors, and returns collected stats. `sandboxesForListPodSandboxStatsRequest` applies ID, label, and ready-state filtering.

## Control Flow

Filtering happens before concurrency. Each goroutine writes to its own index in `stats` and `errs`, then the response compacts non-nil stats after the wait group completes.

## State and Persistence Behavior

No state is mutated except in-place normalization of the filter ID through shared list helpers.

## Dependencies and Integration Points

It integrates with sandbox store filtering, platform stats collection, `ttrpc.ErrClosed`, errdefs, and CRI stats list API.

## Risks and Test Signals

Risks include high goroutine fan-out on many sandboxes and suppressed transient errors hiding recurring stats issues. Tests should cover filtering and joined error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_other.go -->
# sources/cloud-native/containerd/internal/cri/server/sandbox_stats_other.go

## Purpose

This non-Linux, non-Windows file marks pod sandbox stats unsupported.

## Important APIs, Types, and Functions

`podSandboxStats` returns `pod sandbox stats not implemented` wrapping `errdefs.ErrNotImplemented`.

## Control Flow

The function is a direct error return.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform-specific stats symbol under `!windows && !linux`.

## Risks and Test Signals

Clients on these platforms receive a not-implemented stats error. Build-tag compile tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_other.go -->
