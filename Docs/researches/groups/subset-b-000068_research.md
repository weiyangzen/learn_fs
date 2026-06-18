# subset-b-000068 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_stop_test.go

## Purpose

This test file covers selected stop-path helpers in the CRI server package. It verifies that `waitContainerStop` observes timeout, cancellation, and already-finished container states, and it validates CRI signal-name conversion for stop signals and realtime signal spellings.

## Important APIs, Types, and Functions

The file defines `TestWaitContainerStop`, `TestCRISignalToOCIStopSignal`, and `TestConvertFromCRISignal`. The tests use `newTestCRIService`, `containerstore.NewContainer`, `containerstore.WithFakeStatus`, `criService.waitContainerStop`, `criSignalToOCIStopSignal`, and `convertFromCRISignal`. Runtime signal constants come from `k8s.io/cri-api/pkg/apis/runtime/v1`.

## Control Flow

`TestWaitContainerStop` builds fake container statuses with started and finished timestamps, inserts a fake container into the test CRI service store, optionally wraps the context with cancellation or timeout, and asserts whether `waitContainerStop` returns an error. The signal tests are table-driven and compare expected string forms for default, standard, realtime-min-plus, realtime-max-minus, and unknown signals.

## State and Persistence Behavior

The tests only manipulate in-memory fake container store state. The relevant observable state is `containerstore.Status.CreatedAt`, `StartedAt`, and `FinishedAt`, which controls whether a container is considered stopped. No runtime task, containerd metadata, or filesystem state is persisted.

## Dependencies and Integration Points

The tests integrate with the CRI server test harness, `containerstore`, and CRI runtime signal enums. They indirectly protect container stop implementations that wait on store status updates and translate CRI stop signals into OCI-compatible stop signal strings.

## Risks and Edge Cases

The timeout test uses a short wall-clock duration and could be scheduler-sensitive if `waitContainerStop` behavior changes. The tests cover signal-name conversion but not actual delivery to task shims. The signal conversion cases include unknown enum values, but they do not exhaust every CRI signal constant.

## Test Signals

Passing tests show `waitContainerStop` returns errors on timeout or canceled context, succeeds for already-finished containers, preserves runtime-default stop signal as an empty OCI override, maps standard signals, and rewrites `SIGRTMINPLUS1`/`SIGRTMAXMINUS1` into `SIGRTMIN+1`/`SIGRTMAX-1`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources.go

## Purpose

This Linux/Windows build file implements the CRI `UpdateContainerResources` RPC. It updates resource limits in the persisted OCI runtime spec, optionally applies them to a running container task, synchronizes the result into the CRI container status, and coordinates with NRI plugin callbacks.

## Important APIs, Types, and Functions

`(*criService).UpdateContainerResources` is the public CRI handler. `(*criService).updateContainerResources` performs the store-transaction work. `updateContainerSpec` marshals an OCI spec with `typeurl.MarshalAny` and updates `containers.Container.Spec` through `containerd.Container.Update`. Platform-specific helpers `updateOCIResource` and `getResources` are supplied by the Linux and Windows files.

## Control Flow

The handler looks up the container, then its sandbox. It blocks NRI plugin sync, lets NRI mutate the Linux resources request, and updates `r.Linux` if NRI returns a replacement. It then uses `container.Status.UpdateSync` to serialize resource changes with container start and with concurrent updates. Inside the transaction, it rejects containers being removed, loads the old OCI spec, creates a cloned and patched spec, writes it to containerd metadata, and defers rollback if later work fails.

If the container is not running, the spec update is enough because the runtime will consume the new spec at start. If it is running, the code loads the task and calls `task.Update(ctx, containerd.WithResources(getResources(newSpec)))`. `NotFound` from task lookup or update is treated as an already-exited race and not fatal. On success, the new spec is copied into CRI status resources.

## State and Persistence Behavior

The persistent mutation is the containerd metadata `Spec` field. Runtime state is mutated only when a task still exists and is running. CRI store state is updated through the container status transaction after successful spec/task update. On errors after spec write, the deferred rollback attempts to restore the old spec using a deferred context, but rollback failure is logged rather than returned.

## Dependencies and Integration Points

The code depends on containerd client containers and tasks, `typeurl`, OCI runtime spec, CRI runtime API types, `containerstore`, NRI plugin integration, and errdefs. It integrates with Linux and Windows platform resource mappers and with `copyResourcesToStatus` in `helpers.go`.

## Risks and Edge Cases

Spec update and task update are not a single runtime transaction. The rollback path can fail, leaving metadata ahead of task state. `NotFound` is intentionally ignored for exited tasks, which avoids false failures but can hide races if a task disappears unexpectedly. NRI only receives Linux resources in the top-level handler, while Windows resources depend on the platform-specific spec mapper.

## Test Signals

Useful coverage includes started and not-started containers, task `NotFound` races, spec rollback on task-update failure, removal-in-progress rejection, NRI mutation and post-update errors, and status resource copying for both Linux and Windows. The adjacent Linux test validates the platform spec patching behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux.go

## Purpose

This Linux-specific file converts CRI Linux container resource updates into OCI Linux resource fields. It supplies the platform hooks used by the shared `UpdateContainerResources` implementation.

## Important APIs, Types, and Functions

`updateOCIResource` deep-copies the supplied OCI spec, ensures `spec.Linux` exists, and applies `opts.WithResources`. `getResources` returns `spec.Linux.Resources` for `containerd.WithResources`.

## Control Flow

The function clones the old spec with `util.DeepCopy` so callers can roll back safely and so failed updates do not mutate the caller's object. It initializes `cloned.Linux` if absent, then delegates detailed field mapping to `opts.WithResources`, passing hugetlb controller compatibility settings from `criconfig.Config`. It returns the cloned patched spec or an error annotated as a Linux resource-setting failure.

## State and Persistence Behavior

This file has no direct persistence. It creates an in-memory OCI spec copy. The caller persists the result into containerd metadata and applies `spec.Linux.Resources` to a running task.

## Dependencies and Integration Points

Dependencies include OCI runtime spec, CRI runtime API, CRI config, CRI opts, and CRI util deep copy. It integrates directly with `container_update_resources.go` and with `copyResourcesToStatus`, which later translates the same OCI resource fields back to CRI status.

## Risks and Edge Cases

Deep-copy failure aborts the update. Missing `spec.Process` may matter for OOM score changes handled by `opts.WithResources`. Hugetlb controller tolerance changes behavior on hosts lacking controllers. Empty CRI fields are treated as patch semantics by the opts layer, so preserving existing values depends on that helper.

## Test Signals

`container_update_resources_linux_test.go` verifies full updates, skipped empty fields, filling missing resource groups, and patching unified cgroup v2 maps. Additional useful tests would cover hugetlb-related options and nil `Process` handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux_test.go

## Purpose

This test file validates Linux OCI spec patching for CRI `UpdateContainerResources`. It focuses on CPU, memory, OOM score, cpuset, and unified cgroup resource maps.

## Important APIs, Types, and Functions

The central test is `TestUpdateOCILinuxResource`. It calls `updateOCIResource` with fake OCI specs and `runtime.UpdateContainerResourcesRequest` values, then compares the returned spec with an expected OCI spec. It uses `criopts.SwapControllerAvailable` to account for host-dependent swap controller availability.

## Control Flow

Each table case builds an input spec, a CRI request, and an expected cloned spec. The test config enables tolerance for missing hugetlb controllers. After calling `updateOCIResource`, the test asserts error presence and structural equality of the resulting spec.

## State and Persistence Behavior

All state is in-memory. The tests verify the clone output, not the shared RPC handler's metadata persistence, task update, or status transaction behavior.

## Dependencies and Integration Points

Dependencies include OCI runtime spec, protobuf pointer helpers, CRI runtime API, CRI config, and CRI opts. The expected swap field is host-aware because the underlying resource mapper only sets swap when the swap controller is available.

## Risks and Edge Cases

The test assumes host controller detection for swap, so expected output changes by environment in a controlled way. It does not assert that the input spec remains unmodified after cloning. It does not cover invalid cpuset strings, hugetlb limits, nil process, or task application.

## Test Signals

The test proves the Linux mapper updates all major resource fields, preserves unspecified fields, fills missing CPU and unified fields, and patches unified maps without dropping unrelated existing keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_other.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_other.go

## Purpose

This non-Linux, non-Windows build file provides a stub `UpdateContainerResources` implementation for unsupported platforms. It preserves CRI API availability while making no platform resource changes.

## Important APIs, Types, and Functions

The only exported behavior is `(*criService).UpdateContainerResources`. It uses `containerStore.Get` and `container.Status.Update` but does not inspect CRI resource fields or update an OCI spec.

## Control Flow

The handler resolves the requested container ID. If not found, it returns a wrapped error. It then runs a container status update transaction that returns the status unchanged and returns an empty `UpdateContainerResourcesResponse`.

## State and Persistence Behavior

No resource state is changed. The status transaction may still serialize with other store operations, but it returns the same status. No containerd metadata, runtime task, NRI hook, or filesystem state is touched.

## Dependencies and Integration Points

The file depends only on context, fmt, CRI runtime API types, and `containerstore`. It is selected by the `!windows && !linux` build constraint and keeps the CRI server package compiling on other platforms.

## Risks and Edge Cases

Callers receive success even though resource updates are effectively ignored. That is a compatibility choice but can be surprising if kubelet or tests expect an unimplemented error. Because it has no NRI integration, plugins cannot observe unsupported-platform resource updates.

## Test Signals

Useful tests would assert that unsupported builds return success for existing containers, error for missing containers, and leave status/resources/spec unchanged.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_windows.go

## Purpose

This Windows-specific file maps CRI Windows resource updates into OCI Windows resource fields for the shared `UpdateContainerResources` handler.

## Important APIs, Types, and Functions

`updateOCIResource` deep-copies an OCI spec, ensures `spec.Windows` exists, and applies `opts.WithWindowsResources`. `getResources` returns `spec.Windows.Resources` for runtime task update.

## Control Flow

The mapper clones the supplied spec with `util.DeepCopy`, initializes the Windows subsection when missing, and calls the CRI opts helper to apply CRI Windows resource values. Errors are wrapped with Windows resource context. The shared handler persists and applies the returned spec.

## State and Persistence Behavior

This file only constructs an in-memory cloned spec. Containerd metadata updates, task resource updates, and CRI status synchronization are owned by `container_update_resources.go`.

## Dependencies and Integration Points

It depends on OCI runtime spec, CRI runtime API, CRI config, CRI opts, and CRI util. It integrates with `copyResourcesToStatus`, which knows how to project Windows CPU shares/count/maximum, memory limit, and CPU affinity back into CRI status.

## Risks and Edge Cases

Windows resource support differs from Linux and is delegated to `opts.WithWindowsResources`. Missing or unsupported resource fields may silently preserve previous values depending on the opts helper. The shared top-level NRI call currently passes Linux resources, so Windows-specific NRI resource mutation is not represented here.

## Test Signals

Direct tests should mirror the Linux mapper tests for CPU shares/count/maximum, memory limit, affinity, nil `Windows` spec initialization, empty-field preservation, and task update using `spec.Windows.Resources`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events.go -->
# sources/cloud-native/containerd/internal/cri/server/events.go

## Purpose

This file implements CRI-server handling for containerd task, sandbox, OOM, and image events. It updates CRI in-memory stores, cleans up runtime tasks, emits CRI container event responses, and reconciles image metadata after image create/update/delete events.

## Important APIs, Types, and Functions

Key functions are `startSandboxExitMonitor`, `handleSandboxExit`, `startContainerExitMonitor`, `handleContainerExit`, `(*criEventHandler).HandleEvent`, `oomMetricsEventOccurred`, and `getPlatformFromSandboxID`. The `handleEventTimeout` constant limits event handling to ten seconds.

## Control Flow

The per-sandbox and per-container exit monitors wait on a `containerd.ExitStatus` channel or context cancellation. On exit, they build an event object, create a namespaced timeout context, look up the sandbox or container, and call the corresponding handler. Handler failures are logged and pushed into the event monitor backoff queue.

`handleSandboxExit` marks the sandbox not-ready, clears PID, records exit status and time, closes the sandbox stop channel, and emits a CRI stopped event. `handleContainerExit` attaches container IO if present, optionally checks cgroup OOM metrics for Linux exit code 137, deletes the task with NRI exit options and process kill, performs a task-service delete fallback on `NotFound` to avoid shim leaks, updates container status to exited, clears unknown state, stops the container store object, and emits a CRI stopped event.

`criEventHandler.HandleEvent` dispatches containerd events by concrete type. Task exits are matched first against containers by `ID`, then sandboxes. Task OOM updates container reason to `OOMKilled`. Image create/update/delete events call `UpdateImage`.

## State and Persistence Behavior

The file mutates in-memory sandbox and container store statuses. It deletes runtime task state and may call the containerd task service to remove stale shim records. It also drives image-store reconciliation through `UpdateImage`. CRI container event responses are placed on `containerEventsQ`; if status lookup fails, pod status may be nil while container status failures are logged.

## Dependencies and Integration Points

Dependencies include containerd client tasks, task-service API, containerd event types, cgroup v1/v2 metrics, sandbox and container stores, NRI, CRI runtime API, containerd `typeurl`, and platform lookup through `sandboxService.SandboxPlatform`. It integrates with the generic event monitor in `server/events`, image service update logic, and container stop/wait channels.

## Risks and Edge Cases

Event handling is serial in the monitor and uses a fixed timeout; slow task deletion can trigger retry and leak risks. `TaskExit.ID` is used to avoid treating exec exits as container exits. OOM detection has known races with systemd cgroup garbage collection and with asynchronous TaskOOM event handling. Task-service fallback handles one shim leak class but depends on correct `NotFound` classification. The code deliberately ignores missing containers/sandboxes because events can outlive store entries.

## Test Signals

Strong tests would cover monitor-generated exit events, backoff on handler failure, `TaskExit` dispatch to container versus sandbox, OOM reason update from both `TaskOOM` and cgroup metrics, task delete `NotFound` fallback to task-service delete, unknown-to-exited state transition, CRI event queue emission, and image event calls into `UpdateImage`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events.go -->
# sources/cloud-native/containerd/internal/cri/server/events/events.go

## Purpose

This package implements a generic containerd event monitor used by the CRI server. It subscribes to containerd events, filters to the Kubernetes containerd namespace, converts protobuf events into concrete Go event types, invokes an injected handler, and retries failed events with per-object exponential backoff.

## Important APIs, Types, and Functions

The public surface is `EventHandler`, `EventMonitor`, `NewEventMonitor`, `(*EventMonitor).Subscribe`, `(*EventMonitor).Start`, `(*EventMonitor).Backoff`, and `(*EventMonitor).Stop`. Internal retry machinery is `backOff`, `backOffQueue`, `convertEvent`, `newBackOff`, `enBackOff`, `deBackOff`, `reBackOff`, `getExpiredIDs`, and `isInBackOff`.

## Control Flow

`Subscribe` stores the event and error channels returned by a containerd `events.Subscriber`. `Start` starts the backoff ticker and a goroutine selecting over event channel, subscription error channel, backoff expiration ticker, and monitor context cancellation. Events outside the Kubernetes namespace are ignored. Supported event payloads are unpacked with `typeurl.UnmarshalAny`; unsupported event types are logged and skipped.

If an event ID is already in backoff, the new event is appended to that ID's queue. Otherwise, the handler is called immediately; failures enqueue the event. When a queue expires, the monitor drains events in order. If any event fails, the remaining suffix is requeued with doubled duration capped at five minutes.

## State and Persistence Behavior

All state is in memory: subscribed channels, cancellation context, backoff queues keyed by container/sandbox/image ID, queue expiration times, and ticker. There is no persistence across process restarts.

## Dependencies and Integration Points

The package depends on containerd event envelopes, CRI namespace constants, containerd API event types, `typeurl`, logging, and `k8s.io/utils/clock` for testable timing. The CRI server injects `criEventHandler` to mutate CRI stores and image metadata.

## Risks and Edge Cases

`Start` assumes event channels are initialized; starting before subscribe is only safe if only backoff events are used. A receive from a closed channel can yield nil values, so subscriber lifecycle behavior matters. Backoff queues are per ID, preventing event reordering for one object but not across objects. Handler failures during a retry requeue only the unprocessed suffix.

## Test Signals

Tests should validate namespace filtering, conversion keys for every supported event type, immediate handling, queueing while in backoff, expiration-based drain, duration doubling and max cap, subscription errors, stop behavior, and nil or unsupported event payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events_test.go -->
# sources/cloud-native/containerd/internal/cri/server/events/events_test.go

## Purpose

This test file covers the generic event monitor backoff queue behavior and verifies that a monitor can handle pre-enqueued backoff events without a real subscriber.

## Important APIs, Types, and Functions

It defines `noopEventHandler` with `HandleEvent`, `TestEventMonitor_SubscribeNothing`, and `TestBackOff`. The tests use `eventtypes.TaskOOM`, `typeurl.MarshalAny`, `convertEvent`, fake clocks, and protobuf comparison helpers.

## Control Flow

`TestEventMonitor_SubscribeNothing` creates a monitor, starts it without subscribing to containerd, manually enqueues a TaskOOM event into backoff, waits for it to be delivered to the noop handler, stops the monitor, and expects a clean error-channel close. `TestBackOff` uses a fake clock to enqueue two queues, assert their initial state, verify `isInBackOff`, advance time, drain expired queues, prove second drain is nil, and verify `reBackOff` doubles duration and keeps only a suffix.

## State and Persistence Behavior

The tests manipulate only in-memory monitor state. Fake clock control makes backoff expiration deterministic. No containerd event stream, CRI store, or filesystem state is used.

## Dependencies and Integration Points

Dependencies include containerd API event types, `typeurl`, `prototestutil.Compare`, `go-cmp`, `testify/assert`, and `testingclock`. The tests protect behavior used by `criService` event handling but do not exercise the CRI-specific handler.

## Risks and Edge Cases

`TestEventMonitor_SubscribeNothing` has long timeout ceilings and depends on the real backoff ticker interval. The tests do not cover subscriber errors, namespace filtering, unsupported events, or handler failures during drain.

## Test Signals

Passing tests show that backoff queues preserve event contents, report membership correctly, expire based on the configured clock, can be drained once, and can be requeued with doubled duration after partial failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events_test.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_linux.go

## Purpose

This Linux-specific helper file provides Linux implementations for security feature checks, container log opening, robust recursive removal with mount cleanup, SELinux label adjustment for VM-based runtimes, cgroup mode detection, and user-namespace snapshot remap options.

## Important APIs, Types, and Functions

Key functions are `(*criService).apparmorEnabled`, `(*criService).seccompEnabled`, `openLogFile`, `unmountRecursive`, `ensureRemoveAll`, `isVMBasedRuntime`, `modifyProcessLabel`, `isUnifiedCgroupsMode`, and `snapshotterRemapOpts`. The `vmbasedRuntimes` list currently recognizes Kata-style runtime type substrings.

## Control Flow

AppArmor returns false when disabled in config and otherwise delegates to host support detection. Seccomp delegates to runtime support detection. `openLogFile` creates parent directories and opens append-only logs with mode `0640`. `unmountRecursive` canonicalizes a target, finds all mounts under it, sorts deepest first, and uses detached unmounts. `ensureRemoveAll` first attempts recursive unmount, then retries `os.RemoveAll`, treating subpath `ENOENT` races as retryable and attempting detached unmount on `EBUSY` paths up to 50 times.

`modifyProcessLabel` leaves non-VM runtimes unchanged; VM-based runtimes convert the SELinux process label to a KVM label. `snapshotterRemapOpts` parses user namespace mappings and, for pod user namespace mode, emits `containerd.WithRemapperLabels`.

## State and Persistence Behavior

The file performs filesystem mutations through directory creation, log file creation, unmounts, and recursive removal. It does not persist CRI store state. Snapshotter remap options are returned to callers for snapshot metadata labeling.

## Dependencies and Integration Points

Dependencies include Linux cgroups, mountinfo, containerd mount helpers, snapshots options, AppArmor/seccomp helpers, SELinux utilities, CRI runtime API, and OCI specs. The functions are used by container lifecycle cleanup, log setup, sandbox/container security setup, and user namespace snapshot handling.

## Risks and Edge Cases

`ensureRemoveAll` is intentionally aggressive and can hide transient cleanup races, but wrong target paths would be destructive. Detached unmounts may defer cleanup. VM runtime detection is substring-based. Snapshot remapping supports only the single mapping line allowed by shared userns parsing. Security feature probes depend on host capabilities and configuration.

## Test Signals

Existing shared tests cover `ensureRemoveAll` for nonexistent paths, directories, and files. Stronger Linux-specific signals would include mount cleanup with busy mounts, AppArmor disabled config, SELinux KVM relabeling, cgroup v1/v2 detection, and remapper label output for pod user namespaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_other.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_other.go

## Purpose

This non-Linux, non-Windows helper file supplies simple fallback implementations for platform hooks required by the shared CRI server code.

## Important APIs, Types, and Functions

It defines `openLogFile`, `ensureRemoveAll`, `modifyProcessLabel`, and `isUnifiedCgroupsMode` for platforms matching `!windows && !linux`.

## Control Flow

`openLogFile` opens or creates the target path in append-write mode with `0640` permissions but does not create parent directories. `ensureRemoveAll` delegates directly to `os.RemoveAll`. `modifyProcessLabel` is a no-op, and `isUnifiedCgroupsMode` always returns false.

## State and Persistence Behavior

The only mutations are log file creation/opening and recursive filesystem removal through the standard library. No CRI store or runtime state is touched.

## Dependencies and Integration Points

The file depends on context, os, and OCI specs. It keeps the shared CRI server package buildable on unsupported Unix-like platforms where Linux security, mount, and cgroup behavior does not apply.

## Risks and Edge Cases

Unlike Linux, parent directories are not created before opening logs. Removal has no busy-mount handling. Returning false for unified cgroups and leaving labels unchanged are conservative but may omit platform capabilities if a future non-Linux platform gains equivalents.

## Test Signals

Platform-specific tests should verify log open behavior, parent-directory expectations, nonexistent-path removal, and no-op process label semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_test.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_test.go

## Purpose

This test file covers shared CRI server helper behavior around image user parsing, runtime option generation and decoding, OCI environment deduplication, recursive removal basics, PID namespace target validation, Windows resource projection, and Linux host-network detection.

## Important APIs, Types, and Functions

Tests include `TestGetUserFromImage`, `TestGenerateRuntimeOptions`, `TestEnvDeduplication`, `TestEnsureRemoveAllNotExist`, `TestEnsureRemoveAllWithDir`, `TestEnsureRemoveAllWithFile`, helper `addContainer`, `TestValidateTargetContainer`, `TestGetRuntimeOptions`, `TestCopyResourcesToStatusWindowsAffinity`, and `TestHostNetwork`.

## Control Flow

The tests are table-driven. Runtime options are generated from TOML configs and compared to runc option structs. Env deduplication uses `oci.WithEnv` repeatedly to verify later values replace earlier values without reordering unaffected keys. Target-container validation builds fake containers with running, stopped, missing, and cross-sandbox conditions. Host networking is skipped unless running on Linux.

## State and Persistence Behavior

The tests use temporary files/directories and in-memory fake CRI stores. Runtime option tests decode configuration into memory only. No real containerd runtime tasks are created.

## Dependencies and Integration Points

Dependencies include CRI runtime API, containerd CRI config, container store, OCI helper package, runc options, TOML decoding, typeurl, and test assertion libraries. The tests protect helper behavior used by container creation, sandbox setup, resource status reporting, and runtime configuration handling.

## Risks and Edge Cases

Coverage is broad but shallow for several helpers. SELinux label parsing, cgroup path construction, user namespace parsing, CRI event generation, and image reference conversion are not covered here. Host network coverage is Linux-only in this file; Windows has a separate test file.

## Test Signals

Passing tests confirm user/group truncation, numeric UID detection, nil and typed-nil runtime options, environment override semantics, safe basic removal, PID namespace target validation, Windows CPU affinity copy, and Linux namespace-mode host network detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_windows.go

## Purpose

This Windows-specific helper file implements container log opening with Windows sharing semantics, long-path normalization, simple recursive removal, and no-op platform hooks for process labels and cgroups.

## Important APIs, Types, and Functions

The key functions are `openLogFile`, `fixLongPath`, `ensureRemoveAll`, `modifyProcessLabel`, and `isUnifiedCgroupsMode`.

## Control Flow

`openLogFile` first converts the path through `fixLongPath`, rejects an empty path, converts it to UTF-16, and calls `syscall.CreateFile` with `OPEN_ALWAYS`, append-data access, and read/write/delete sharing. Delete sharing is important so kubelet can rotate container logs while the runtime still has the file open.

`fixLongPath` is copied from Go's Windows filepath logic. It returns short paths unchanged, leaves UNC and relative paths unchanged, and for long absolute paths without `..` elements builds the `\\?\` extended-length form while normalizing separators and `.` elements. `ensureRemoveAll` delegates to `os.RemoveAll`. Label modification is a no-op and unified cgroup mode is false.

## State and Persistence Behavior

The file mutates filesystem state by opening or creating log files and removing directories. It does not persist CRI store state or runtime metadata.

## Dependencies and Integration Points

Dependencies include Windows syscalls, os, filepath, and OCI specs. The log open behavior integrates with CRI container logging and kubelet log rotation on Windows.

## Risks and Edge Cases

The low-level `CreateFile` path must stay aligned with Go and Windows behavior. Long-path conversion deliberately skips relative paths, UNC paths, and paths with `..`, which may leave some long paths unmodified. `ensureRemoveAll` lacks Linux-style busy mount handling, which is appropriate for Windows but means cleanup behavior differs by platform.

## Test Signals

The adjacent Windows test covers host-network logic rather than this file. Useful tests would cover `fixLongPath` short/long/relative/UNC cases and log opening with delete-sharing during simulated rotation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows_test.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_windows_test.go

## Purpose

This Windows-only test file validates the Windows branch of `hostNetwork`, where host networking is determined by HostProcess pod configuration.

## Important APIs, Types, and Functions

The file defines `TestWindowsHostNetwork`, which calls the shared `hostNetwork` helper with `runtime.PodSandboxConfig` values containing `WindowsSandboxSecurityContext.HostProcess`.

## Control Flow

The table-driven test checks three cases: explicit `HostProcess: false`, explicit `HostProcess: true`, and an empty Windows security context. It compares the helper result to the expected boolean for each case.

## State and Persistence Behavior

There is no persistent or mutable state. The test builds CRI config structs in memory.

## Dependencies and Integration Points

The test depends on CRI runtime API types and the shared `hostNetwork` helper. It protects sandbox networking decisions for Windows HostProcess pods.

## Risks and Edge Cases

The test does not cover nil `PodSandboxConfig`, nil `Windows` config, or nil security context beyond the empty security context object. It does not exercise actual CNI or HostProcess runtime behavior.

## Test Signals

Passing tests show that Windows HostProcess pods are treated as host-network pods and that false or absent HostProcess settings do not request host networking.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/check.go -->
# sources/cloud-native/containerd/internal/cri/server/images/check.go

## Purpose

This file implements startup-style image readiness checking for the CRI image service. It scans containerd images, verifies content readiness and unpack status, and refreshes the CRI in-memory image store for usable images.

## Important APIs, Types, and Functions

The primary function is `(*CRIImageService).CheckImages`. It uses `c.client.ListImages`, `images.Check`, `containerd.Image.IsUnpacked`, and `c.UpdateImage`.

## Control Flow

`CheckImages` lists images from the containerd client. For each image, it starts a wait-group goroutine that checks content availability for the default platform, warns and skips if content is incomplete, checks whether the image is unpacked for the configured snapshotter, warns if not unpacked, and calls `UpdateImage` to reconcile CRI image metadata. Per-image errors are logged but do not cause `CheckImages` to fail after the initial list succeeds.

## State and Persistence Behavior

The function can update the CRI image store through `UpdateImage`, which may create CRI-managed references and refresh in-memory metadata. It does not pull missing content or unpack images; it only logs readiness problems.

## Dependencies and Integration Points

Dependencies include containerd image checks, platform matching, logging, and the CRI image service's client and config. It integrates with image-service startup recovery, image event reconciliation, and the in-memory `imagestore`.

## Risks and Edge Cases

The implementation currently checks only the default snapshotter and default platform. It logs but does not repair incomplete content or missing unpacked snapshots. Running checks concurrently can amplify load on content and metadata stores. The use of `sync.WaitGroup.Go` depends on the Go version/library in this tree.

## Test Signals

Useful tests would cover list failure, content check errors, content incomplete, unpack check errors, unpack missing, successful `UpdateImage`, and per-image error isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_fuzz_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_fuzz_test.go

## Purpose

This fuzz test exercises `ParseAuth` against arbitrary CRI `AuthConfig` structures and host strings to find panics or unexpected crashes in auth parsing.

## Important APIs, Types, and Functions

The file defines `FuzzParseAuth`. It uses `github.com/AdaLogics/go-fuzz-headers` to populate a `runtime.AuthConfig` and host string, then calls `ParseAuth`.

## Control Flow

For each fuzz input, the consumer attempts to generate an auth struct and a host. If either generation step fails, the input is skipped. Otherwise, `ParseAuth` is called and its returned username, secret, and error are intentionally ignored.

## State and Persistence Behavior

The fuzz target has no persistent state. It only constructs data in memory and calls the parser.

## Dependencies and Integration Points

Dependencies include the CRI runtime API and the local `ParseAuth` implementation in `image_pull.go`. This fuzz target complements table tests for known auth formats.

## Risks and Edge Cases

Because return values are ignored, the fuzz test catches panics and severe parser issues but not semantic regressions. It depends on struct generation quality to reach combinations such as malformed base64, invalid server URLs, identity tokens, and username/password mixtures.

## Test Signals

Useful fuzz findings would include panics on malformed URLs or base64, unexpected memory growth from decoded auth length handling, and unsafe handling of unusual host strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_list.go

## Purpose

This file implements CRI `ListImages` for the gRPC image service wrapper. It exposes images known to the CRI in-memory image store as CRI runtime image records.

## Important APIs, Types, and Functions

The only function is `(*GRPCCRIImageService).ListImages`. It calls `c.imageStore.List` and converts each `imagestore.Image` using `toCRIImage`.

## Control Flow

The handler ignores request filters, retrieves all images from the in-memory store, appends converted CRI images to a slice, and returns a `runtime.ListImagesResponse`.

## State and Persistence Behavior

The function is read-only. It does not verify containerd content or snapshot existence at list time and does not refresh the image store.

## Dependencies and Integration Points

Dependencies include context and CRI runtime API. It integrates with `image_status.go` for conversion logic and with `imagestore.Store`, which is refreshed by pulls, startup checks, and image events.

## Risks and Edge Cases

The handler may report stale images if content or snapshots are removed outside CRI after the in-memory store was updated. CRI list filters are not implemented. Image order follows store order and is not explicitly sorted.

## Test Signals

`image_list_test.go` verifies conversion of IDs, repo tags, repo digests, size, numeric UID, and username values for multiple fake images.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_list_test.go

## Purpose

This test file validates CRI `ListImages` conversion from internal image-store entries to CRI runtime image records.

## Important APIs, Types, and Functions

The file defines `TestListImages`. It uses `newTestCRIService`, `imagestore.NewFakeStore`, `(*GRPCCRIImageService).ListImages`, and `toCRIImage` indirectly.

## Control Flow

The test builds three fake images with tag and digest references, sizes, and image config users. It installs them into the service's fake image store, calls `ListImages`, checks the returned count, and asserts that all expected CRI image objects are present.

## State and Persistence Behavior

All state is in memory in the fake image store. No containerd metadata or snapshots are consulted.

## Dependencies and Integration Points

Dependencies include image-spec types, CRI runtime API, the CRI image store package, and test assertion libraries. The test protects the list handler and shared image conversion logic.

## Risks and Edge Cases

The test does not assert response ordering, filter behavior, pinned images, empty references, or stale snapshot/content handling. It assumes `ParseImageReferences` splits the provided references into expected tag and digest arrays.

## Test Signals

Passing tests prove that image ID, repo tags, repo digests, size, numeric UID, and username fields are represented correctly in list responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_pull.go

## Purpose

This file implements CRI image pulling, registry authentication and mirror configuration, CRI-managed image reference creation, image-store refresh, image pull metrics, encrypted image pull options, snapshotter selection, and progress-timeout reporters for both local `client.Pull` and containerd transfer-service pulls.

## Important APIs, Types, and Functions

Public and high-value functions include `(*GRPCCRIImageService).PullImage`, `(*CRIImageService).PullImage`, `pullImageWithLocalPull`, `pullImageWithTransferService`, `ParseAuth`, `createOrUpdateImageReference`, `getLabels`, `UpdateImage`, `hostDirFromRoots`, `registryHosts`, `toRuntimeAuthConfig`, `defaultScheme`, `addDefaultScheme`, `registryEndpoints`, `encryptedImagesPullOpts`, `snapshotterFromPodSandboxConfig`, and `newCRICredentials`.

Progress-related types include `pullProgressReporter`, `pullRequestReporter`, `pullRequestReporterRoundTripper`, `countingReadCloser`, and `transferProgressReporter`.

## Control Flow

The gRPC handler builds a credential callback from request auth or host config and delegates to `CRIImageService.PullImage`. The service increments in-progress metrics, normalizes the image reference with Docker reference parsing, parses the configured progress timeout, selects a snapshotter from the runtime handler or deprecated sandbox annotation, prepares CRI labels including pinned-image labels, and chooses either local pull or transfer service based on config.

The local pull path creates a Docker resolver with CRI registry hosts and a progress-reporting HTTP client wrapper, then calls `client.Pull` with resolver, snapshotter, unpack, labels, concurrency, download limiter, unpack duplication suppressor, syncfs, optional encrypted-image unpack options, optional snapshot annotations, and optional child-label filtering for discarded unpacked layers. The transfer path constructs a transfer image store with platform/unpack/labels, creates a registry with CRI credentials, headers, and host config path, starts transfer progress reporting, calls `transferrer.Transfer`, and then resolves the image from containerd.

After a successful pull, the service obtains the config digest as image ID, computes repo tag and repo digest, creates or updates references for image ID, tag, and digest, refreshes the CRI image store for each, records throughput, logs, and returns the image ID. `UpdateImage` reconciles containerd image events, adding CRI-managed labels and an ID reference when needed before updating the in-memory store.

## State and Persistence Behavior

Successful pulls persist image metadata references in containerd's image store, unpack snapshots through the selected snapshotter, and update the CRI in-memory image store. Metrics counters, gauges, and histograms are updated around the pull. Progress reporters maintain in-memory counters and cancel the pull context when active requests stop making byte progress. No direct content deletion occurs except via child GC label configuration when discarding unpacked layers.

## Dependencies and Integration Points

Dependencies include containerd client pull APIs, image/content stores, transfer service, Docker resolver/config, registry credential helper, image encryption, CRI config, CRI labels and annotations, tracing, metrics, platform selection, snapshotter helpers, distribution reference parsing, and CRI runtime API. The file is central to kubelet `PullImage`, startup image cache recovery, and image event reconciliation.

## Risks and Edge Cases

The comments document a fundamental split between containerd metadata/content and CRI's ready-only in-memory index. Failed pulls can leave containerd metadata not represented as CRI-ready. `createOrUpdateImageReference` is not atomic across create/get/update and can race with external deletion. Transfer service currently lacks support for several local-pull options noted in TODOs. Progress timeout logic must distinguish idle periods from active no-progress requests. Auth matching depends on parsed `ServerAddress` host and ignores registry token. Snapshotter selection still supports a deprecated annotation fallback.

## Test Signals

Tests cover auth forms and server matching, mirror endpoint defaults and wildcard precedence, default scheme selection, encrypted pull option count, runtime-handler snapshotter selection and annotation fallback, pinned labels, transfer progress accounting and timeout, and local pull progress cancellation semantics. Integration tests are still needed for actual pull/unpack/reference behavior across local and transfer paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_pull_test.go

## Purpose

This test file covers image pull support logic: registry auth parsing, registry mirror endpoint construction, default scheme choice, encrypted pull options, snapshotter selection from runtime handler or annotation, pinned-image labels, and progress reporter behavior.

## Important APIs, Types, and Functions

Tests include `TestParseAuth`, `TestRegistryEndpoints`, `TestDefaultScheme`, `TestEncryptedImagePullOpts`, `TestSnapshotterFromPodSandboxConfig`, `TestImageGetLabels`, `TestTransferProgressReporter`, and `TestPullProgressReporter`.

## Control Flow

Auth tests exercise nil, empty, identity token, username/password, base64 auth, invalid auth, and server-address matching. Endpoint tests configure mirror maps and assert default endpoint addition, wildcard behavior, host-specific precedence, missing scheme handling, localhost HTTP defaults, and paths. Snapshotter tests configure runtime-specific snapshotter mappings and validate precedence of the explicit runtime handler over the deprecated annotation.

Progress reporter tests feed synthetic transfer progress events and assert active request and byte counts, ignored malformed progress nodes, completion without explicit complete events, timeout cancellation, and multiple concurrent nodes. Local pull progress tests manually increment request and bytes counters to prove stuck requests are canceled and progressing requests are not.

## State and Persistence Behavior

All tests use in-memory service config, maps, fake contexts, and reporter counters. They do not contact registries, write image metadata, or unpack snapshots.

## Dependencies and Integration Points

Dependencies include CRI runtime API, CRI config, CRI labels/annotations, containerd transfer progress types, image-spec descriptors, platform defaults, base64 encoding, time, and assertion libraries.

## Risks and Edge Cases

The tests validate support functions but not full `PullImage` success or failure with containerd. Progress timeout tests use real timers and short sleeps, which can be sensitive under high load. Encrypted pull option test currently only checks option count, not functional decryption.

## Test Signals

Passing tests provide strong regression signals for auth precedence, mirror endpoint compatibility, snapshotter-selection compatibility with older clients, pinned image labeling, and the no-progress cancellation bug class called out in the comments.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_remove.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_remove.go

## Purpose

This file implements CRI image removal. It resolves an image by reference or ID, deletes all known references from containerd's image store, and refreshes the CRI in-memory image index.

## Important APIs, Types, and Functions

`(*GRPCCRIImageService).RemoveImage` is the CRI gRPC handler. `(*CRIImageService).RemoveImage` performs resolution and deletion. It uses `LocalResolve`, `c.images.Delete`, `images.SynchronousDelete`, and `c.imageStore.Update`.

## Control Flow

The gRPC wrapper delegates to the service and suppresses `NotFound` as CRI success. The service resolves the image locally. Missing images are traced and treated as success. For each known reference, it deletes the reference from containerd; the last reference uses synchronous delete to trigger garbage collection. After successful or already-missing deletion, it updates the in-memory image store for that reference.

## State and Persistence Behavior

The function deletes containerd image metadata references and may trigger best-effort garbage collection on the last reference. It refreshes CRI image-store state to reflect removed references. It does not directly delete content blobs or snapshots.

## Dependencies and Integration Points

Dependencies include containerd core images store APIs, errdefs, tracing, and CRI runtime API. It integrates with `LocalResolve` and the image store maintained by pulls and image events.

## Risks and Edge Cases

Reference deletion can race with external image store changes. Synchronous deletion is best effort and only applied to the last reference known in the in-memory image object. If updating the CRI image store after a delete fails, removal returns an error even if containerd metadata changed.

## Test Signals

Useful tests would cover missing image success, partial reference deletion failures, `NotFound` during delete, synchronous option on last reference, image-store update failures, and concurrent reference removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_status.go

## Purpose

This file implements CRI `ImageStatus` and conversion of internal CRI image metadata into CRI `runtime.Image` and optional verbose info.

## Important APIs, Types, and Functions

Key functions are `(*CRIImageService).ImageStatus`, `toCRIImage`, package-local `getUserFromImage`, `verboseImageInfo`, and `(*CRIImageService).toCRIImageInfo`.

## Control Flow

`ImageStatus` resolves the requested image locally. `NotFound` returns an empty response with no error. Other resolution errors are wrapped. For found images, it converts the image to CRI fields, optionally builds verbose info, and returns both. `toCRIImage` splits references into repo tags and repo digests, copies ID, size, pinned flag, and converts image config user into either `Uid` or `Username`. Verbose info JSON includes chain ID and the OCI image spec under the `"info"` map key.

## State and Persistence Behavior

The file is read-only. It does not verify snapshot/content readiness at status time and does not refresh image-store metadata.

## Dependencies and Integration Points

Dependencies include JSON encoding, CRI runtime API, image-spec, CRI image store, CRI util reference parsing, errdefs, and logging. The conversion helper is also used by `ListImages`.

## Risks and Edge Cases

Returning empty success for missing images matches CRI semantics but can hide stale references. Verbose JSON marshal errors are logged and returned as the info string rather than failing the status call. `getUserFromImage` ignores group fields and treats only the substring before `:`. Snapshot readiness is a TODO.

## Test Signals

Existing tests cover missing image response, found image conversion, and user parsing for numeric, username, empty, and multi-separator forms. Additional tests should cover verbose info, pinned images, marshal failure behavior, and stale snapshot/content conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_status_test.go

## Purpose

This test file validates CRI image status conversion and image user parsing in the image service package.

## Important APIs, Types, and Functions

Tests are `TestImageStatus` and `TestGetUserFromImage`. They use `newTestCRIService`, `imagestore.NewFakeStore`, `(*CRIImageService).ImageStatus`, `(*GRPCCRIImageService).ImageStatus`, and `getUserFromImage`.

## Control Flow

`TestImageStatus` first queries a missing image ID and expects an empty successful response. It then installs a fake image with tag and digest references, size, chain ID, and config user, calls image status through the gRPC wrapper, and compares the expected CRI image. `TestGetUserFromImage` is table-driven over numeric and named users with optional group components.

## State and Persistence Behavior

All state is held in a fake in-memory image store. There are no containerd metadata, content, or snapshot operations.

## Dependencies and Integration Points

Dependencies include CRI runtime API, image-spec, CRI image store, and assertion libraries. The tests protect code used by both image status and image list responses.

## Risks and Edge Cases

Verbose image info is not tested. Pinned status and empty references are not covered. The missing image path only validates local store miss behavior, not containerd store reconciliation.

## Test Signals

Passing tests confirm CRI-compatible missing image semantics and correct conversion of ID, repo tag, repo digest, size, and username/UID fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info.go -->
# sources/cloud-native/containerd/internal/cri/server/images/imagefs_info.go

## Purpose

This file implements CRI `ImageFsInfo`, aggregating cached snapshot usage into filesystem usage entries grouped by snapshotter.

## Important APIs, Types, and Functions

The primary function is `(*CRIImageService).ImageFsInfo`. It reads `c.snapshotStore.List`, groups by `snapshotter`, and emits `runtime.FilesystemUsage` entries with mountpoints from `c.imageFSPaths`.

## Control Flow

The function walks cached snapshots and aggregates size and inode counts per snapshotter while preserving the oldest timestamp in each group. It emits the default snapshotter first for kubelet compatibility. If the default snapshotter has no cached usage, it emits a zero-usage entry with the current timestamp. It then appends entries for remaining snapshotters.

## State and Persistence Behavior

The function is read-only over cached snapshot usage. The cache is maintained asynchronously by `snapshotsSyncer`. It does not query the content store or live snapshotters directly and does not persist state.

## Dependencies and Integration Points

Dependencies include CRI snapshot store and CRI runtime API. It integrates with kubelet image filesystem stats and with the snapshot syncer started by `NewService`.

## Risks and Edge Cases

Content store disk usage is explicitly not counted. Windows usage is noted as unsupported. Snapshotter map iteration order for non-default snapshotters is not deterministic. Missing `imageFSPaths` entries can yield empty mountpoints.

## Test Signals

The adjacent test verifies aggregation, oldest timestamp selection, default snapshotter first-entry behavior, and mountpoint mapping for a non-default snapshotter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/imagefs_info_test.go

## Purpose

This test file validates image filesystem usage aggregation from cached snapshot usage entries.

## Important APIs, Types, and Functions

It defines `TestImageFsInfo`, using `newTestCRIService`, `snapshotstore.Snapshot`, `(*GRPCCRIImageService).ImageFsInfo`, and CRI `FilesystemUsage`.

## Control Flow

The test adds three overlayfs snapshots with active, committed, and view kinds, different sizes, inode counts, and timestamps. It calls `ImageFsInfo`, expects two entries because the service also emits the default snapshotter entry first, and asserts that the overlayfs entry sums size and inodes and uses the oldest timestamp.

## State and Persistence Behavior

The test uses only the in-memory snapshot store. No live snapshotter usage calls or filesystem stat calls occur.

## Dependencies and Integration Points

Dependencies include containerd snapshot kind constants, CRI snapshot store, CRI runtime API, and assertion libraries. The test protects kubelet-facing imagefs stats behavior.

## Risks and Edge Cases

The test does not validate zero default snapshotter details, multiple non-default snapshotter ordering, missing mountpoint mapping, or content-store usage omission.

## Test Signals

Passing tests confirm per-snapshotter aggregation and timestamp selection in image filesystem stats.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/imagefs_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/metrics.go -->
# sources/cloud-native/containerd/internal/cri/server/images/metrics.go

## Purpose

This file declares and registers image-pull metrics for the CRI image service under the `containerd_cri_sandboxed` metric namespace/subsystem.

## Important APIs, Types, and Functions

Metrics are package variables: `imagePulls`, `inProgressImagePulls`, and `imagePullThroughput`. The `init` function creates a docker/go-metrics namespace, constructs a labeled counter for pull success/failure, a gauge for in-progress pulls, and a Prometheus histogram for pull throughput, then registers the namespace.

## Control Flow

At package initialization, the namespace and metric collectors are created and registered. Runtime pull code increments or decrements the gauge, increments the labeled counter by outcome, and observes throughput after successful pull size and duration are known.

## State and Persistence Behavior

Metrics are process-local Prometheus/docker-go-metrics collectors. They are not persisted by this file, but external metrics scraping observes their current values.

## Dependencies and Integration Points

Dependencies are `github.com/docker/go-metrics` and Prometheus client_golang. Integration points are `image_pull.go` and the containerd metrics registry.

## Risks and Edge Cases

Metric registration in `init` can conflict if package initialization happens more than once in unusual test setups. Throughput uses default histogram buckets, which may not fit all image-pull speeds. The status counter currently labels only success and failure, with a TODO for registry domain labels.

## Test Signals

Useful tests would verify registration, counter/gauge updates around successful and failed pulls, and throughput observation on success without adding duplicate collectors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service.go -->
# sources/cloud-native/containerd/internal/cri/server/images/service.go

## Purpose

This file defines the CRI image service core type, construction options, gRPC wrapper, runtime snapshotter mapping, local image resolution, and accessors for image and snapshot metadata.

## Important APIs, Types, and Functions

Important types are `imageClient`, `ImagePlatform`, `CRIImageService`, `GRPCCRIImageService`, and `CRIImageServiceOptions`. Key functions are `NewService`, `UpdateRuntimeSnapshotter`, `LocalResolve`, `RuntimeSnapshotter`, `GetImage`, `GetSnapshot`, `ImageFSPaths`, `Config`, and `GRPCService`.

## Control Flow

`NewService` creates an optional download semaphore from config, initializes the CRI image store, snapshot store, runtime platform mapping, transfer service, unpack keyed locker, and other dependencies, then starts a background snapshots syncer. `UpdateRuntimeSnapshotter` lazily initializes the runtime-platform map and adds a runtime mapping only when one does not already exist. `LocalResolve` treats valid digests as image IDs; otherwise it normalizes Docker references and resolves them through the in-memory image store, falling back to treating the input as an image ID. `RuntimeSnapshotter` returns the runtime override when set, otherwise the default image snapshotter.

## State and Persistence Behavior

The service owns in-memory image and snapshot stores, runtime-platform mappings, download limiter, and snapshot syncer. Persistent containerd image/content/snapshot state is accessed through injected stores and clients; this file initializes the wrappers but does not itself persist image metadata.

## Dependencies and Integration Points

Dependencies include containerd client image APIs, content/images/snapshot stores, transfer service, CRI config, CRI image and snapshot stores, keyed locks, semaphores, Docker reference parsing, digests, platform defaults, and CRI runtime API. It is the construction and dependency-injection hub for all files in `server/images`.

## Risks and Edge Cases

`NewService` assumes non-nil options fields that later methods require. `LocalResolve` silently returns empty string on parse/resolve errors before falling back to ID lookup, which can obscure why a reference failed. `UpdateRuntimeSnapshotter` intentionally does not override existing mappings. The snapshots syncer starts an untracked goroutine with no stop hook.

## Test Signals

Existing tests cover local resolution across many Docker reference forms and runtime snapshotter override behavior. Additional tests should cover service construction with nil dependencies, download limiter creation, runtime mapping non-overwrite behavior, and snapshot syncer interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/service_test.go

## Purpose

This test file provides the image service test harness and validates local image resolution and runtime-specific snapshotter selection.

## Important APIs, Types, and Functions

It defines constants `testImageFSPath` and `testSandboxImage`, helper `newTestCRIService`, `testImageConfig`, `TestLocalResolve`, and `TestRuntimeSnapshotter`.

## Control Flow

`newTestCRIService` builds a `CRIImageService` with fake image and snapshot stores, an empty runtime platform map, and test config, returning both core and gRPC wrapper objects. `TestLocalResolve` installs one fake busybox image with Docker-qualified references and asserts that digest ID, short names, tagged names, digest references, library-prefixed names, and Docker-qualified forms all resolve to the same image. A random ID is expected to return `NotFound`. `TestRuntimeSnapshotter` checks default and runtime override cases.

## State and Persistence Behavior

All state is in-memory fake stores and config structs. No snapshot syncer, content store, registry, or containerd client is used by these tests.

## Dependencies and Integration Points

Dependencies include CRI config, image and snapshot stores, errdefs, platform defaults, and assertion libraries. The helper is reused by other image package tests.

## Risks and Edge Cases

The test harness omits several real service dependencies, so methods that require client, images store, content store, or transfer service need additional setup. Local resolve tests do not cover invalid Docker reference parse diagnostics or multiple images sharing references.

## Test Signals

Passing tests prove Docker reference normalization behavior and default-versus-runtime snapshotter selection for the image service.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/snapshots.go -->
# sources/cloud-native/containerd/internal/cri/server/images/snapshots.go

## Purpose

This file implements a background snapshot usage syncer that periodically caches snapshot size and inode usage for imagefs and container stats consumers.

## Important APIs, Types, and Functions

The main type is `snapshotsSyncer` with constructor `newSnapshotsSyncer`, methods `start` and `sync`, and helper `calculateEMA`.

## Control Flow

`start` launches a goroutine that repeatedly calls `sync`, logs errors, measures cycle cost, computes a smoothed target sleep with an exponential moving average, enforces a minimum sleep of half the configured period, and sleeps before the next cycle. `sync` uses a namespaced context, records a start timestamp, walks each configured snapshotter to collect snapshot infos, queries usage outside the walk callback, updates existing non-active snapshot timestamps cheaply, fetches usage for new or active snapshots, stores size/inode data, and deletes cached snapshots not updated during the cycle.

## State and Persistence Behavior

The syncer maintains an in-memory `snapshotstore.Store`. It reads live snapshotter metadata and usage, but it does not write containerd snapshot metadata. Stale cache entries are deleted when not observed in the latest sync.

## Dependencies and Integration Points

Dependencies include containerd snapshotter APIs, CRI snapshot store, CRI namespaced context utility, errdefs, and logging. It is started by `NewService` and feeds `ImageFsInfo` plus any stats code reading the snapshot store.

## Risks and Edge Cases

The goroutine has no stop mechanism and can continue until process exit. Usage calls can be expensive and have TODOs for timeouts. Non-active snapshots reuse previous size/inode values and only refresh timestamps, so long-lived committed snapshot usage changes may not be detected. If sync takes longer than the period, minimum sleep still releases CPU but effective frequency drops.

## Test Signals

Useful tests would cover EMA sleep calculation, snapshot walk failure, usage failure and `NotFound` handling, active snapshot usage refresh, non-active timestamp-only update, stale cache deletion, and multiple snapshotter keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/snapshots.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors.go -->
# sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors.go

## Purpose

This file declares the CRI metric descriptor constants and descriptor objects used by `ListMetricDescriptors` and by the Linux pod sandbox metrics collector. It defines the names, help text, and label keys for CPU, memory, network, disk, disk IO, process, miscellaneous, and container spec metrics.

## Important APIs, Types, and Functions

It exports category constants such as `CPUUsageMetrics`, `MemoryUsageMetrics`, `NetworkUsageMetrics`, `DiskIOMetrics`, `DiskUsageMetrics`, `ProcessMetrics`, `MiscellaneousMetrics`, and `ContainerSpecMetrics`. It declares label key slices `baseLabelKeys`, `networkLabelKeys`, and `diskLabelKeys`, plus many `*runtime.MetricDescriptor` variables such as `containerCPUUsageSecondsTotal`, `containerMemoryUsageBytes`, `containerNetworkReceiveBytesTotal`, `containerFsUsageBytes`, `containerProcesses`, and `containerSpecMemoryLimitBytes`.

## Control Flow

There is no executable control flow beyond package initialization of variables. Descriptor arrays with extra labels are built with `append` over copies or base slices for dimensions such as network interface, disk device, failure type, scope, major/minor/operation, and ulimit.

## State and Persistence Behavior

Descriptors are process-global immutable-by-convention pointers. The file stores no metrics values and performs no persistence.

## Dependencies and Integration Points

The file depends on CRI runtime API types. Linux descriptor listing groups these variables in `getMetricDescriptors`, and Linux metric extraction functions use descriptor names and label order when building `runtime.Metric` values.

## Risks and Edge Cases

Because descriptors are mutable pointer values, accidental mutation could affect all responses and emitted metrics. Label order must stay aligned with `ListPodSandboxMetrics` extraction code. The help text and metric names should remain compatible with consumers expecting cAdvisor-like metrics.

## Test Signals

Useful tests would verify descriptor name uniqueness, expected label key order, descriptor categories matching emitted metric names, and no accidental mutation between calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_linux.go

## Purpose

This Linux-specific file implements CRI `ListMetricDescriptors`, returning the static descriptor set supported by Linux pod sandbox metrics collection.

## Important APIs, Types, and Functions

The public handler is `(*criService).ListMetricDescriptors`. The helper `(*criService).getMetricDescriptors` returns a map from category constants to descriptor slices.

## Control Flow

The handler gets the descriptor map, appends all category slices into one flat slice, and returns it in `runtime.ListMetricDescriptorsResponse`. The category map includes CPU, memory, network, disk usage, disk IO, process, miscellaneous, and container spec descriptors.

## State and Persistence Behavior

The handler is read-only and returns pointers to package-level descriptor objects. It does not collect metric values or mutate CRI/containerd state.

## Dependencies and Integration Points

Dependencies include context and CRI runtime API. It integrates with the Linux `ListPodSandboxMetrics` implementation and with kubelet or metrics consumers that first discover descriptors.

## Risks and Edge Cases

Map iteration order is not deterministic, so descriptor response order can vary. Returning shared descriptor pointers means caller-side mutation would be unsafe if not treated as read-only. Non-Linux platforms intentionally use a different unimplemented handler.

## Test Signals

Useful tests would assert that every emitted Linux metric has a descriptor, that descriptor names are unique, that all expected categories are present, and that order-insensitive clients handle the response.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_other.go -->
# sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_other.go

## Purpose

This non-Linux build file implements `ListMetricDescriptors` as an unimplemented CRI method on unsupported platforms.

## Important APIs, Types, and Functions

The only function is `(*criService).ListMetricDescriptors`, returning a gRPC status error with code `Unimplemented`.

## Control Flow

The handler ignores request contents and immediately returns nil response plus `status.Errorf(codes.Unimplemented, ...)`.

## State and Persistence Behavior

No state is read or mutated.

## Dependencies and Integration Points

Dependencies include context, gRPC status/codes, and CRI runtime API. The file is selected for `!linux` builds and complements the Linux implementation.

## Risks and Edge Cases

Metrics descriptor discovery is unavailable on non-Linux platforms even where some metrics might theoretically be collectable. Clients must handle gRPC unimplemented.

## Test Signals

Platform-specific tests should assert the exact `codes.Unimplemented` status and nil response.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics.go -->
# sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics.go

## Purpose

This file is an otherwise empty package participant for pod sandbox metrics. It keeps the package source layout stable while platform-specific files provide the actual `ListPodSandboxMetrics` implementations.

## Important APIs, Types, and Functions

There are no functions, types, constants, or variables in this file beyond `package server`.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The file has no state or persistence behavior.

## Dependencies and Integration Points

It has no imports. The meaningful integration is with build-tagged files: Linux supplies the full implementation, and non-Linux supplies an unimplemented RPC handler.

## Risks and Edge Cases

The file can look accidental because it has no declarations. Its main risk is confusion for maintainers searching for the metrics implementation.

## Test Signals

Compilation is the only direct signal. Functional tests belong to the platform-specific implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_linux.go

## Purpose

This Linux-specific file implements CRI `ListPodSandboxMetrics`. It collects pod-level network metrics and container-level CPU, memory, disk IO, filesystem, process, ulimit, and spec resource metrics from containerd tasks, cgroup v1/v2 stats, rootfs usage, and `/proc`.

## Important APIs, Types, and Functions

Key functions are `(*criService).ListPodSandboxMetrics`, `collectPodSandboxMetrics`, `collectContainerMetrics`, `extractCPUMetrics`, `extractMemoryMetrics`, `extractDiskIOMetrics`, `extractProcessMetrics`, `extractContainerSpecMetrics`, `findContainerTaskRootfs`, `extractFilesystemMetrics`, and `getContainerProcessDescriptorCount`. A package-level rate limiter and errgroup concurrency limit both cap concurrent collection at ten.

## Control Flow

The handler applies the containerd namespace to context, precomputes a sandbox-to-containers map from the container store, then iterates ready sandboxes. For each ready sandbox it waits on a rate limiter and starts an errgroup task. The task builds base pod labels, collects sandbox network metrics from the sandbox network namespace when present, then collects each associated container's metrics. Transient unavailable/not-found errors are logged and skipped; cancellation stops collection; other per-object errors are logged while returning partial results.

Container metrics load the container task, call `task.Metrics`, unmarshal cgroup v1 or v2 stats with `typeurl`, build label values, add last-seen and start-time metrics, then independently append CPU, memory, disk IO, filesystem, process, and spec metrics. Each extractor logs and allows partial metric output if it fails.

CPU and memory extraction normalize cgroup v1 nanoseconds and cgroup v2 microseconds into seconds-like counters, and map cgroup-specific fields into descriptor names. Disk IO maps blkio or cgroup v2 IO stats into read/write counters. Process metrics include pids, thread limits, ulimit soft values, and `/proc/<pid>/fd` descriptor/socket counts. Filesystem metrics infer the task rootfs path from containerd state layout, stat the filesystem, and prefer snapshotter usage when available.

## State and Persistence Behavior

The implementation is read-only over CRI stores, containerd tasks, cgroup metrics, snapshot usage, rootfs stats, and `/proc`. It returns a snapshot of metrics and does not persist counters. It logs partial failures but still returns collected metrics.

## Dependencies and Integration Points

Dependencies include cgroup v1/v2 stats, containerd task APIs, CRI stores, sandbox store, snapshot service, network namespace stats helper `getContainerNetIO`, CRI descriptor variables, NRI name for bundle path construction, errgroup, rate limiter, and Linux `/proc`/`statfs`. It integrates with `ListMetricDescriptors` via shared descriptor names and label order.

## Risks and Edge Cases

The rootfs finder is explicitly described as inherently broken because task specs use relative root paths; it reconstructs a containerd bundle path from state dir, runtime plugin, namespace/name, and container ID. Filesystem device labels are acknowledged as wrong. Start time uses `StartedAt` nanoseconds as a gauge named seconds, which may need scrutiny. Cgroup v1/v2 field semantics differ, and some v2 values are zero-filled for unavailable v1-style counters. Returning partial results can mask systemic collection failures.

## Test Signals

Useful tests should cover ready-sandbox filtering, partial-result behavior, cgroup v1 and v2 CPU/memory/IO mappings, network namespace metrics, process fd/socket counting, ulimit extraction, spec metric extraction, rootfs inference failures, snapshot usage fallback, descriptor coverage, rate limiting, and cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_other.go -->
# sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_other.go

## Purpose

This non-Linux build file marks CRI `ListPodSandboxMetrics` as unsupported on non-Linux platforms.

## Important APIs, Types, and Functions

The only function is `(*criService).ListPodSandboxMetrics`, which returns a gRPC `Unimplemented` status.

## Control Flow

The function ignores the request and immediately returns nil response plus `status.Errorf(codes.Unimplemented, "ListPodSandboxMetrics not implemented on this platform")`.

## State and Persistence Behavior

No CRI, runtime, cgroup, or filesystem state is read or changed.

## Dependencies and Integration Points

Dependencies include context, gRPC status/codes, and CRI runtime API. It complements the Linux implementation selected by build tags.

## Risks and Edge Cases

Metrics collection is unavailable on non-Linux even for platforms that may expose some analogous data. Clients must handle gRPC unimplemented cleanly.

## Test Signals

Platform-specific tests should check the unimplemented status code and nil response.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/metrics.go -->
# sources/cloud-native/containerd/internal/cri/server/metrics.go

## Purpose

This file declares and registers CRI server operation metrics for sandbox, container, checkpoint, and network plugin operations.

## Important APIs, Types, and Functions

Package metrics include timers for sandbox list/network create/network delete, labeled timers for sandbox runtime create/stop/remove, container create/start/stop/remove/checkpoint, a container-events-dropped counter, and labeled counters/timers for network plugin operations and errors. Constants `networkStatusOp`, `networkSetUpOp`, and `networkTearDownOp` preserve dockershim-compatible operation labels.

## Control Flow

The `init` function creates a `containerd_cri` metrics namespace, initializes every metric collector with names, help strings, and labels, then registers the namespace.

## State and Persistence Behavior

Metrics are process-local collectors registered with docker/go-metrics. The file does not persist values but exposes them for the containerd metrics endpoint.

## Dependencies and Integration Points

The only import is `github.com/docker/go-metrics`. Other CRI server files observe or increment these metrics around lifecycle and network plugin operations.

## Risks and Edge Cases

Registration happens at package initialization and can conflict in unusual test configurations if duplicate namespaces are registered. Metric names and labels are compatibility-sensitive, especially network operation labels kept for kubelet/dockershim compatibility.

## Test Signals

Useful tests would verify metrics registration, expected names/labels, and that lifecycle paths record timers and counters without duplicate collector errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri.go -->
# sources/cloud-native/containerd/internal/cri/server/nri.go

## Purpose

This file adapts `criService` to the internal NRI implementation interface by exposing CRI configuration, stores, metadata extension keys, and sandbox metadata access.

## Important APIs, Types, and Functions

It defines `criImplementation` with methods `Config`, `SandboxStore`, `ContainerStore`, `ContainerMetadataExtensionKey`, and `SandboxMetadataStore`.

## Control Flow

Every method is a direct accessor over the embedded `*criService`. `Config` returns the address of the service config. Store accessors return sandbox/container stores and the containerd sandbox metadata store. The metadata extension key returns the CRI labels constant for container metadata.

## State and Persistence Behavior

The adapter does not mutate state itself. It hands NRI access to live service stores and config, so callers can read or mutate through those returned objects depending on their APIs.

## Dependencies and Integration Points

Dependencies include containerd sandbox store interfaces, CRI config, CRI labels, and CRI container/sandbox stores. This adapter is used by NRI integration code to interact with CRI-managed state without depending directly on the full `criService` type.

## Risks and Edge Cases

Returning a pointer to `criService.config` exposes mutable configuration to interface consumers. Store access must respect the stores' concurrency contracts. Interface expansion requires platform-specific methods such as the Linux file's resource-update and stop-container hooks.

## Test Signals

Useful tests would assert that accessors return the exact service stores/config and correct metadata extension key, and that NRI callers can use the adapter without data races.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/nri_linux.go

## Purpose

This Linux-specific file adds NRI adapter methods that let NRI invoke CRI container resource updates and container stop behavior through existing `criService` implementations.

## Important APIs, Types, and Functions

It defines `(*criImplementation).UpdateContainerResources` and `(*criImplementation).StopContainer`.

## Control Flow

`UpdateContainerResources` delegates to `i.c.updateContainerResources`, passing the container, request, and current status supplied by NRI integration. `StopContainer` delegates to `i.c.stopContainerRetryOnConnectionClosed` with a timeout.

## State and Persistence Behavior

State changes are performed by the delegated CRI service methods. Resource updates can mutate containerd spec metadata, running task resources, and CRI container status. Stop can signal and wait for runtime task shutdown. This adapter file itself stores no state.

## Dependencies and Integration Points

Dependencies include context, time, CRI container store, and CRI runtime API. It integrates NRI plugin actions with the CRI server's native resource-update and stop-container code paths on Linux.

## Risks and Edge Cases

Because this delegates into shared CRI logic, NRI-triggered changes inherit the same race and rollback behavior as normal CRI calls. Stop behavior depends on retry handling for connection-closed errors in code outside this file. The file is Linux-only, so equivalent NRI hooks are unavailable on non-Linux builds.

## Test Signals

Useful tests would use fake `criService` state to verify that NRI adapter calls reach the underlying update and stop methods, propagate errors, and preserve status updates consistently with direct CRI RPC paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri_linux.go -->
