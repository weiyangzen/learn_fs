# Research Group subset-b-000064

This grouped report covers containerd CRI integration tests for container lifecycle, logging, stats, resource updates, image handling, volumes, failpoint binaries, NRI behavior, pod networking/hostname/user namespace behavior, and issue-specific regressions. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_exec_test.go -->
# sources/cloud-native/containerd/integration/container_exec_test.go

## Purpose

This integration test verifies CRI `ExecSync` IO draining behavior after an exec process exits while leaving background children alive. It targets a regression-prone container lifecycle edge where the exec command returns, but inherited stdout/stderr pipes may remain open and block CRI response completion.

## Important APIs, Types, And Functions

- `TestContainerDrainExecIOAfterExit` is the only test entry point.
- Shared helpers `PodSandboxConfigWithCleanup`, `ContainerConfig`, `WithCommand`, and `EnsureImageExists` create a long-lived BusyBox container.
- `runtimeService.ExecSync` drives the actual exec calls and checks timeout/error behavior.

## Control Flow

The test skips Windows because detached process behavior differs there. It creates a sandbox and a BusyBox container running `sleep 365d`, then starts the container. It first executes `sh -c "sleep 365d &"` with a five-second timeout and requires an error containing `failed to drain exec process`, proving CRI does not hang forever when IO remains open. It then executes `sleep 2s &` with a longer timeout and expects success, proving short-lived inherited IO can be drained before the timeout.

## State And Persistence Behavior

All state is transient: a sandbox, container, and exec processes. Cleanup removes and stops the container through deferred CRI calls. The behavioral state under test is not persisted data but shim/exec pipe lifecycle after exec command completion.

## Dependencies And Integration Points

The file depends on the CRI runtime service, the shared integration helper layer, and the configured BusyBox image from `integration/images`. It integrates with containerd shim exec handling and CRI timeout/error propagation.

## Risks And Edge Cases

The assertions are timing-sensitive and depend on shell background job behavior. A too-small timeout could become flaky on slow hosts, while a too-large timeout slows failure detection. The error-string check couples the test to CRI error wording.

## Test Signals

Passing confirms that stuck exec IO is surfaced as a timeout/error and that drainable short-lived background process IO completes successfully.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_io_leak_linux_test.go -->
# sources/cloud-native/containerd/integration/container_io_leak_linux_test.go

## Purpose

This Linux integration test checks that a failed container start does not leak pipe file descriptors in the shim. It targets cleanup behavior after `runc` start failure, especially when the configured process command cannot be found.

## Important APIs, Types, And Functions

- `TestContainerIOLeakAfterStartFailed` creates a container with a nonexistent command and checks shim pipe count after start failure.
- `numPipe` shells out to `lsof -p <shimPid> | grep pipe` and counts matching lines.
- The test reuses `getShimPid` from the TTY leak test and `connectToShim`/`shimPid` from the issue 7496 helpers.

## Control Flow

The test skips non-runc `RUNC_FLAVOR` values because it is specifically probing runc shim behavior. It starts a sandbox, ensures BusyBox exists, creates a container whose command is `something-that-doesnt-exist`, records the shim PID before start, expects `StartContainer` to fail, and then asserts that `numPipe(pid)` is zero.

## State And Persistence Behavior

No durable state is intentionally changed. The state under test is the shim process file descriptor table after a failed `StartContainer`. Sandbox cleanup is provided by `PodSandboxConfigWithCleanup`.

## Dependencies And Integration Points

The test depends on Linux, runc, `lsof`, a running shim, CRI `CreateContainer`/`StartContainer`, and the ttrpc shim connection helpers. It observes containerd indirectly through host process inspection.

## Risks And Edge Cases

`lsof` availability and permissions are host-dependent. Counting grep output can miss pipes if `lsof` format changes. The test assumes the shim remains alive after the failed start long enough to inspect it.

## Test Signals

Passing indicates failed start cleanup closes exec/stdio pipes in the shim instead of leaving descriptors pinned.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_io_leak_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_log_test.go -->
# sources/cloud-native/containerd/integration/container_log_test.go

## Purpose

This file validates CRI container log formatting for edge cases around partial lines and maximum log line splitting. It ensures containerd writes Kubernetes CRI log lines with timestamps, streams, tags, and payloads in the expected shape.

## Important APIs, Types, And Functions

- `TestContainerLogWithoutTailingNewLine` verifies output without a trailing newline is tagged as `P`/partial.
- `TestLongContainerLog` verifies lines at `MaxContainerLogLineSize - 1`, exactly at max, and over max are tagged/split correctly.
- `checkContainerLog` parses log lines and validates RFC3339Nano timestamps plus expected CRI stream/tag/message fields.
- `CRIConfig` provides the configured max log line size.

## Control Flow

Each test creates a temporary pod log directory, starts a sandbox with `WithPodLogDirectory`, creates a BusyBox container with `WithLogPath`, waits until the container exits, reads the log file, and checks its lines. The long-line test constructs shell loops that print repeated characters to exercise full and partial line behavior.

## State And Persistence Behavior

The relevant persisted state is the pod log file under the temporary log directory. The test does not mutate long-lived containerd state beyond normal sandbox/container creation and cleanup.

## Dependencies And Integration Points

It depends on CRI log configuration, CRI runtime status polling, BusyBox shell behavior, and `k8s.io/cri-api` constants for stream and log tag names. It also integrates with the shared `CRIConfig` helper, which reads verbose CRI status.

## Risks And Edge Cases

The test is sensitive to exact log tag semantics and max-size configuration. The shell loop uses `printf` without quoting the payload character, which is safe for the fixed characters used here. It assumes log writing is complete by the time container state is `EXITED`.

## Test Signals

Passing confirms CRI logs preserve partial final lines, split oversized lines, and use parseable timestamps and expected tags.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_restart_test.go -->
# sources/cloud-native/containerd/integration/container_restart_test.go

## Purpose

This file verifies basic CRI restart workflows for normal containers and containers that failed to start. It ensures a stopped/removed container can be recreated with the same metadata in the same sandbox.

## Important APIs, Types, And Functions

- `TestContainerRestart` starts a Pause container, stops/removes it, recreates it with the same config, and starts it again.
- `TestFailedContainerRestart` creates a bad-command container, expects start failure, removes it, then creates a valid replacement.
- Shared helper APIs provide sandbox/container config construction and cleanup.

## Control Flow

Both tests create a sandbox, ensure the Pause image exists, build a `ContainerConfig`, and call CRI `CreateContainer`/`StartContainer`. The successful restart path explicitly stops and removes the first container before recreating. The failed-start path expects `StartContainer` to fail, then still calls stop/remove before recreating with a corrected config.

## State And Persistence Behavior

The tests exercise CRI metadata cleanup and name reuse inside a sandbox. The key state transition is from created/running or created/failed to removed, followed by a new container record with the same name.

## Dependencies And Integration Points

They depend on CRI runtime lifecycle calls, the image helper package, and containerd metadata cleanup. They integrate with name uniqueness handling because reuse must only succeed after removal.

## Risks And Edge Cases

The failed-start test defers `StopContainer` even after a failed start; this is tolerated by the integration helper expectations but could hide differences in runtime handling of stopped/non-started containers. The tests do not inspect old task or snapshot cleanup directly.

## Test Signals

Passing shows that container metadata and runtime state are clean enough after normal removal and failed starts to allow same-name recreation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_restart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_stats_test.go -->
# sources/cloud-native/containerd/integration/container_stats_test.go

## Purpose

This file validates CRI container stats retrieval, stats filtering, live memory consumption reporting, writable layer accounting, and sysfs mount behavior for privileged combinations. It covers both single-container and list/filter stats APIs.

## Important APIs, Types, And Functions

- `TestContainerStats` checks `ContainerStats` for one running container.
- `TestContainerConsumedStats` uses a resource-consumer image and `ExecSync` to increase memory usage.
- `TestContainerListStats`, `TestContainerListStatsWithIdFilter`, `TestContainerListStatsWithSandboxIdFilter`, and `TestContainerListStatsWithIdSandboxIdFilter` validate `ListContainerStats` filtering, including truncated IDs.
- `testStats` centralizes metadata, CPU, memory, and writable-layer assertions.
- `TestContainerSysfsStatsWithPrivilegedPod` validates sysfs `rw`/`ro` behavior for pod/container privileged combinations.

## Control Flow

The stats tests create sandboxes and multiple containers, then poll with `Eventually` until writable layer or memory timestamps are populated. Filter tests build maps from container IDs to configs and verify returned stats match labels, annotations, metadata, and filesystem fields. The consumed-stats test starts a memory allocation workload and waits for reported working set to rise. The sysfs test table executes `mount | grep sysfs` in containers or expects container creation failure when a privileged container is requested in a non-privileged sandbox.

## State And Persistence Behavior

Runtime stats are live observations from tasks, cgroups, and snapshotter state. No durable state is written except temporary containers and logs. The sysfs test validates generated OCI mount state inside running containers.

## Dependencies And Integration Points

The file integrates with CRI stats APIs, cgroup/memory accounting, snapshot writable-layer accounting, Windows/Linux conditional behavior, and CRI privileged policy. It depends on images `Pause`, `ResourceConsumer`, and `BusyBox`.

## Risks And Edge Cases

Stats are asynchronous and platform-sensitive; Windows has different writable-layer and inode expectations. Memory-increase thresholds can be flaky under tight host memory or slow accounting. The privileged sysfs assertion depends on mount output formatting.

## Test Signals

Passing indicates stats metadata, filtering, resource counters, writable-layer fields, and sysfs privilege rules are exposed correctly through CRI.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_stop_signal_test.go -->
# sources/cloud-native/containerd/integration/container_stop_signal_test.go

## Purpose

This Linux-focused test validates CRI custom stop signal support and default stop signal reporting. It ensures configured stop signals are persisted in container status and are actually used when stopping a container.

## Important APIs, Types, And Functions

- `TestContainerStopSignals` table-tests SIGUSR1, SIGUSR2, SIGHUP, SIGINT, and SIGTERM.
- `TestDefaultContainerStopSignal` checks that containers without custom configuration report `SIGTERM`.
- `writeStopSignalScript` creates a trap script mounted into the container.
- `WithStopSignal`, `WithVolumeMount`, and `WithLogPath` build the test container config.

## Control Flow

The custom-signal test skips Windows, creates a sandbox with host networking and a temporary log directory, writes a shell script that traps a named signal, mounts it, starts the container, checks `ContainerStatus.StopSignal`, stops the container, and verifies exit code zero plus a log line saying the signal was received. The default test starts a sleeping container without `StopSignal`, checks status reports `SIGTERM`, stops it, and checks it exits.

## State And Persistence Behavior

The configured stop signal is stored in container CRI metadata/status. The proof of signal delivery is persisted only in the temporary CRI log file.

## Dependencies And Integration Points

It depends on CRI `StopContainer`, container status stop signal fields, BusyBox shell trap behavior, volume mounts, and CRI log formatting through `checkContainerLog`.

## Risks And Edge Cases

Shell trap names must match BusyBox `sh` behavior. The test assumes the child sleep process is cleaned up by the trap. SELinux or mount restrictions could prevent the generated script from being executable, although it is written with mode `0644` and invoked as `sh /path`.

## Test Signals

Passing confirms both API-level stop-signal reporting and runtime signal delivery behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_stop_signal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_stop_test.go -->
# sources/cloud-native/containerd/integration/container_stop_test.go

## Purpose

This file tests container stop behavior in shared PID namespace scenarios and cancellation behavior when the CRI request context expires before the stop timeout. It protects against incorrect task killing and premature cleanup under cancellation.

## Important APIs, Types, And Functions

- `TestSharedPidMultiProcessContainerStop` covers host PID and pod PID sandbox modes.
- `TestContainerStopCancellation` uses a raw CRI gRPC client to cancel `StopContainer` earlier than its requested timeout.
- Shared helpers `WithHostPid`, `WithPodPid`, `RawRuntimeClient`, `Eventually`, and `Consistently` support the tests.

## Control Flow

The shared-PID test creates sandboxes in host and pod PID modes, starts a BusyBox shell that launches two `sleep` processes, calls `StopContainer` with timeout zero, and asserts the state becomes exited. The cancellation test starts a container that traps and ignores SIGTERM, calls raw `StopContainer` with a one-second context timeout and a three-second CRI stop timeout, expects an error, verifies for five seconds that the container remains running, then stops it normally with a one-second timeout.

## State And Persistence Behavior

The tests observe runtime task state only. The cancellation scenario specifically verifies that a canceled RPC does not asynchronously complete the stronger kill path after the client has gone away.

## Dependencies And Integration Points

They integrate with CRI stop handling, raw gRPC request contexts, PID namespace configuration, and container status reporting. Linux-only cancellation behavior is skipped on Windows.

## Risks And Edge Cases

Timing is central: cancellation must happen before the CRI stop timeout and status must be sampled long enough to catch delayed kills. The shell trap semantics depend on PID 1 behavior inside the container namespace.

## Test Signals

Passing indicates multi-process containers stop correctly in shared PID modes and canceled stop requests leave the container running until a subsequent explicit stop.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_stop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_tty_leak_linux_test.go -->
# sources/cloud-native/containerd/integration/container_tty_leak_linux_test.go

## Purpose

This Linux integration test checks that TTY/PTY descriptors are not leaked by shim exec and container lifecycle operations. It validates both TTY-only and interactive TTY containers.

## Important APIs, Types, And Functions

- `TestContainerTTYLeakAfterExit` runs subtests for `stdin=false` and `stdin=true`.
- `getShimPid` connects to the shim ttrpc API and returns the shim PID.
- `numTTY` counts `ptmx` descriptors with `lsof`.
- `checkTTY` polls for an expected descriptor count.
- Kubernetes `remotecommand` SPDY executor streams the CRI exec session.

## Control Flow

The test creates a BusyBox sandbox, then for each case creates a TTY container running `sleep 365d`. After start, it checks the shim has one TTY. It then requests an exec session with TTY, opens the returned URL using a SPDY executor, streams stdout and optional stdin, and checks the TTY count remains one. Finally it stops/removes the container and checks the count drops to zero.

## State And Persistence Behavior

The only state observed is the shim file descriptor table. Container and exec sessions are transient; cleanup removes the container after each subtest.

## Dependencies And Integration Points

This test integrates CRI `Exec`, kubelet-style SPDY remotecommand streaming, containerd shim ttrpc connection, and host `lsof`. It uses the `k8s.io` containerd namespace when locating the shim.

## Risks And Edge Cases

It depends on host support for `lsof`, permissions to inspect shim FDs, and remotecommand URL availability. Descriptor counts can be affected by concurrent execs if tests are not isolated.

## Test Signals

Passing shows that TTY descriptors are opened for the main container and closed after exec/container removal without accumulating extra PTYs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_tty_leak_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_update_resources_test.go -->
# sources/cloud-native/containerd/integration/container_update_resources_test.go

## Purpose

This Linux test file validates CRI `UpdateContainerResources` behavior for memory and swap limits before and after container start, and verifies that container status reflects updated resources. It cross-checks CRI state, OCI specs, and live cgroup state.

## Important APIs, Types, And Functions

- `checkMemoryLimit`, `checkMemorySwapLimit`, and `checkMemoryLimitInContainerStatus` assert expected spec/status fields.
- `getCgroupSwapLimitForTask` and `getCgroupMemoryLimitForTask` read cgroup v1/v2 stats for a running container task.
- `isSwapLikelyEnabled` gates swap tests based on `/proc/swaps` and cgroup support.
- `TestUpdateContainerResources_MemorySwap`, `TestUpdateContainerResources_MemoryLimit`, and `TestUpdateContainerResources_StatusUpdated` cover swap, memory, and status propagation.

## Control Flow

The swap test skips when swap/accounting is unavailable, creates a container with memory and swap limits, verifies OCI spec fields, starts the task, validates cgroup limits, updates swap, then rechecks spec and cgroup state. The memory-limit test performs a similar sequence around memory limits and default swap mirroring when the swap controller is available. The status test checks `ContainerStatus.Resources.Linux.MemoryLimitInBytes` before start, after update while created, and after update while running.

## State And Persistence Behavior

Resource updates mutate container metadata/OCI spec stored by containerd and live cgroup controller state for running tasks. Status reads reflect persisted CRI container resource fields.

## Dependencies And Integration Points

The file integrates CRI resource APIs, containerd client task/spec access, cgroups v1/v2 libraries, `criopts.SwapControllerAvailable`, and Linux kernel swap accounting.

## Risks And Edge Cases

Swap behavior varies heavily by kernel, cgroup mode, and host configuration. cgroup v2 reports swap as swap limit plus memory usage limit, so assertions encode that API detail. Host controllers with unlimited or disabled limits can cause skips or unexpected values.

## Test Signals

Passing confirms resource updates are written to OCI metadata, applied to live cgroups, and exposed through CRI status.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_update_resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_volume_linux_test.go -->
# sources/cloud-native/containerd/integration/container_volume_linux_test.go

## Purpose

This Linux test validates that containers can run when the overlayfs snapshotter is configured with the `volatile` mount option and image-defined volumes are honored. It specifically exercises kernel support for volatile overlay mounts.

## Important APIs, Types, And Functions

- `TestRunContainerWithVolatileOption` is the sole test entry point.
- `kernelversion.GreaterEqualThan` gates the test to kernel 5.10 or newer.
- `newCtrdProc`, `pullImagesByCRI`, and `newPodTCtx` start an isolated containerd process and run a container against it.

## Control Flow

The test skips old kernels, writes a temporary containerd config enabling CRI image-defined volumes and setting overlayfs `mount_options = ["volatile"]`, starts a separate containerd process from that work directory, registers cleanup for pods and process shutdown, pulls the `VolumeOwnership` image, creates a pod test context, and runs a container executing `sleep 1d`.

## State And Persistence Behavior

It creates an isolated temporary containerd root/state directory and config file. All container and snapshot state is cleaned up with the test containerd process.

## Dependencies And Integration Points

It integrates with containerd process management helpers outside this file, CRI image pull/runtime services, overlayfs snapshotter configuration, kernel version detection, and the `ghcr.io/containerd/volume-ownership` fixture image.

## Risks And Edge Cases

The test assumes overlayfs is the active snapshotter and that the host kernel supports volatile semantics. It only proves container creation/start succeeds; detailed mount-option verification for image volumes is covered in `image_volume_linux_test.go`.

## Test Signals

Passing indicates the CRI/runtime path can create image-defined volumes and containers under overlayfs volatile mount configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_volume_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_volume_test.go -->
# sources/cloud-native/containerd/integration/container_volume_test.go

## Purpose

This cross-platform test verifies that host volume paths involving symlinks are resolved/mounted so the container reads the expected target file. It covers symlinked files, files inside symlinked directories, and symlinked files that point through symlinked directories.

## Important APIs, Types, And Functions

- `createRegularFile` creates the baseline target file.
- `fileInSymlinkedFolder`, `symlinkedFile`, and `symlinkedFileInSymlinkedFolder` construct host path variants.
- `TestContainerSymlinkVolumes` runs the table and validates container log output.

## Control Flow

Each subtest creates temporary log and volume directories, writes `regular/foo.txt`, creates one of the symlink path variants, creates a sandbox with a log directory, ensures BusyBox exists, and starts a container that runs `cat` on the mounted path. After the container exits, the test reads the CRI log and checks it contains the target content. On Windows, the mount path is normalized as a `C:` path.

## State And Persistence Behavior

State is limited to temporary host files/symlinks and the container log. The test checks volume resolution behavior but does not persist any containerd metadata beyond normal lifecycle state.

## Dependencies And Integration Points

It integrates CRI host-path mounts, symlink handling, platform path normalization, BusyBox `cat`, and CRI logging.

## Risks And Edge Cases

Host filesystem symlink permissions or Windows symlink support can affect setup. The test reads log output rather than directly inspecting mount metadata, so failures reflect effective data access but not the exact bind source used.

## Test Signals

Passing means CRI volume mount handling follows symlink paths sufficiently for containers to access the intended file content.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_without_image_ref_test.go -->
# sources/cloud-native/containerd/integration/container_without_image_ref_test.go

## Purpose

This test verifies that a running container remains manageable after its original image reference is removed from CRI image storage. It protects lifecycle operations from depending on a still-present tag/reference after container creation.

## Important APIs, Types, And Functions

- `TestContainerLifecycleWithoutImageRef` is the only test.
- `EnsureImageExists` returns the image ID/reference used for deletion.
- `imageService.RemoveImage`, `runtimeService.ContainerStatus`, and `runtimeService.StopContainer` drive the core behavior.

## Control Flow

The test creates a sandbox, ensures BusyBox is available, creates and starts a sleeping container, removes the image using the returned image ID, then asserts the container remains `RUNNING`. It stops the container and checks the state becomes `EXITED`.

## State And Persistence Behavior

The test mutates CRI image metadata by removing the image reference while preserving container/task state. It depends on snapshots and container metadata retaining enough information to operate without that reference.

## Dependencies And Integration Points

It integrates CRI image and runtime services, image ID/reference handling, and container runtime lifecycle operations.

## Risks And Edge Cases

Removing the shared BusyBox image can affect other tests if they run concurrently against the same CRI instance; the integration suite generally serializes or re-pulls images as needed. The test does not verify subsequent container creation from the removed reference.

## Test Signals

Passing confirms status and stop operations work after image reference deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_without_image_ref_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/containerd_image_test.go -->
# sources/cloud-native/containerd/integration/containerd_image_test.go

## Purpose

This file validates CRI image visibility and metadata when images are manipulated directly through the containerd client rather than CRI. It covers image import into the `k8s.io` namespace, namespace isolation, sandbox image pinning, and externally pulled pause images.

## Important APIs, Types, And Functions

- `TestContainerdImage` pulls BusyBox with `containerdClient.Pull`, waits for CRI visibility, checks labels/pinning, and starts a container by image ID.
- `TestContainerdImageInOtherNamespaces` verifies images in a non-CRI namespace are invisible until CRI pulls its own copy.
- `TestContainerdSandboxImage` checks the pause image exists and is pinned.
- `TestContainerdSandboxImagePulledOutsideCRI` removes/pulls the pause image outside CRI and verifies CRI marks it pinned.

## Control Flow

The main test removes preexisting CRI image state, pulls BusyBox directly with labels including the CRI pinned label, waits for `ImageStatus` by ref and ID, verifies repo tags and managed labels, then creates a container using the image ID. Deferred cleanup deletes both tag and ID references and verifies CRI visibility changes. Namespace isolation uses a `test` containerd namespace to prove CRI does not see images outside `k8s.io`.

## State And Persistence Behavior

These tests mutate containerd image store records and CRI image index state. They specifically check labels such as `io.cri-containerd.image` and pin metadata, and they validate reference deletion behavior.

## Dependencies And Integration Points

The file integrates containerd client image service, CRI image service, namespace scoping, CRI labels, errdefs not-found handling, and runtime container creation.

## Risks And Edge Cases

Tests rely on asynchronous CRI image-store reconciliation and therefore use `Eventually`/`Consistently`. Shared image references can interfere with parallel tests. Label semantics are tightly coupled to CRI image management internals.

## Test Signals

Passing shows containerd-side image changes in the CRI namespace are reflected in CRI, labels/pins are maintained, and namespace isolation is respected.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/containerd_image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/duplicate_name_test.go -->
# sources/cloud-native/containerd/integration/duplicate_name_test.go

## Purpose

This test validates CRI name uniqueness enforcement for pod sandboxes and containers. It ensures duplicate create attempts fail instead of overwriting or aliasing existing objects.

## Important APIs, Types, And Functions

- `TestDuplicateName` is the only test.
- `PodSandboxConfigWithCleanup` creates the first sandbox with metadata.
- `runtimeService.RunPodSandbox` and `runtimeService.CreateContainer` are called twice with the same configs.

## Control Flow

The test creates a sandbox, then attempts to run another sandbox with the same config and requires an error. It ensures the Pause image exists, creates one container in the sandbox, then attempts to create the same container again and requires an error.

## State And Persistence Behavior

The state under test is CRI metadata indexing by sandbox/container names within the relevant scope. No explicit cleanup is needed for the duplicate failures beyond the initial sandbox cleanup.

## Dependencies And Integration Points

It depends on CRI metadata validation and image availability. It integrates with containerd CRI name reservation logic for both sandbox and container records.

## Risks And Edge Cases

The test only checks that an error occurs, not its type or message. It does not test name reuse after removal, which is covered by restart tests.

## Test Signals

Passing confirms duplicate sandbox and container names are rejected while originals exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/duplicate_name_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/cni-bridge-fp/main_linux.go -->
# sources/cloud-native/containerd/integration/failpoint/cmd/cni-bridge-fp/main_linux.go

## Purpose

This Linux CNI plugin wrapper delegates to the standard `bridge` plugin while injecting configurable failpoints for `ADD`, `CHECK`, and `DEL`. It lets integration tests simulate CNI command failures or delays using pod annotations.

## Important APIs, Types, And Functions

- `netConf`, `inheritedPodAnnotations`, and `failpointConf` model CNI stdin config and external failpoint state.
- `main` registers CNI `cmdAdd`, `cmdCheck`, and `cmdDel`.
- `handleFailpoint` extracts `failpoint.cni.containerd.io/confpath` and evaluates command-specific failpoints.
- `failpointControl.delegatedEvalFn` parses and advances failpoint state.
- `updateTx` locks, reads, updates, marshals, and atomically writes the failpoint JSON file.

## Control Flow

Each CNI command first calls `handleFailpoint`. If no absolute config path annotation exists, it proceeds normally. Otherwise it opens the config under `flock`, unmarshals command failpoint strings, constructs a `failpoint.Failpoint`, stores the delegated evaluation function, updates the serialized failpoint state, and evaluates the function. If it succeeds, the wrapper delegates to `bridge` using CNI `invoke` APIs and prints the result for `ADD`.

## State And Persistence Behavior

Failpoint progression is persisted in the JSON file named by pod annotation. `continuity.AtomicWriteFile` makes updates atomic while `flock` serializes concurrent CNI invocations.

## Dependencies And Integration Points

It integrates CNI skel/invoke/version packages, containerd internal failpoint parsing/evaluation, pod annotation inheritance, Unix file locking, and the standard `bridge` CNI plugin.

## Risks And Edge Cases

The config path must be absolute and writable. Invalid JSON or failpoint syntax fails the CNI command. Delegation assumes a `bridge` plugin is installed and discoverable. The file mode `0666` relies on process umask and directory permissions for safety.

## Test Signals

This binary is exercised indirectly by failpoint-backed integration tests that need deterministic CNI command behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/cni-bridge-fp/main_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/main_linux.go -->
# sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/main_linux.go

## Purpose

This small Linux binary starts a failpoint-enabled runc shim manager under runtime type `io.containerd.runc-fp.v1`. It is the executable entry point for tests that need a shim with injected ttrpc task API failures.

## Important APIs, Types, And Functions

- `main` calls `shim.RunShim(context.Background(), manager.NewShimManager("io.containerd.runc-fp.v1"))`.
- The behavior is extended by the package-level plugin registration in `plugin_linux.go`.

## Control Flow

Startup is delegated entirely to containerd's shim runner and runc v2 manager. The custom runtime type name distinguishes this shim from the normal runc runtime so integration test configs can opt into failpoint behavior.

## State And Persistence Behavior

This file does not persist state itself. Runtime state is managed by the shim manager and plugins loaded in the same package.

## Dependencies And Integration Points

It integrates with containerd's `cmd/containerd-shim-runc-v2/manager` and `pkg/shim` packages. The companion plugin registers the task service implementation that injects failpoints.

## Risks And Edge Cases

The runtime type name must match test containerd configuration. If the companion plugin fails to initialize, the shim starts without the expected task failpoint behavior or fails during plugin setup.

## Test Signals

Indirect tests using `failpointRuntimeHandler` validate that this entry point can run a shim and expose the failpoint task service.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/main_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/plugin_linux.go -->
# sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/plugin_linux.go

## Purpose

This Linux shim plugin wraps the runc task ttrpc service with failpoint evaluation driven by OCI annotations. It lets tests inject errors into specific shim task API calls such as `Shutdown`.

## Important APIs, Types, And Functions

- `failpointPrefixKey` is the annotation prefix `io.containerd.runtime.v2.shim.failpoint.`.
- `init` registers a `plugins.TTRPCPlugin` named `task`.
- `taskServiceWithFp` stores parsed failpoints and the real task service.
- `UnaryServerInterceptor` evaluates a failpoint based on the ttrpc method basename before calling the underlying method.
- `newFailpointFromOCIAnnotation` reads `config.json` from the shim bundle and parses prefixed annotations.

## Control Flow

During plugin init, the code obtains the event publisher and shutdown service, reads failpoints from the OCI spec, constructs the normal runc task service, and returns `taskServiceWithFp`. The interceptor extracts the method name from `info.FullMethod`, evaluates a configured failpoint if present, then invokes the real ttrpc method. Registration still exposes the normal task service API.

## State And Persistence Behavior

Failpoint state is initialized from OCI annotations and then held in memory. Individual `Failpoint` objects may mutate internally as they are evaluated. The annotations are persisted in the bundle `config.json` generated for the shim.

## Dependencies And Integration Points

It integrates with containerd plugin registry, shim publisher/shutdown services, runc task service, OCI spec reading, ttrpc interceptors, and internal failpoint syntax.

## Risks And Edge Cases

The shim working directory must be the bundle directory so `config.json` resolves correctly. Annotation method names must match ttrpc method basenames. Invalid failpoint syntax fails shim plugin initialization.

## Test Signals

The skipped shutdown retry test and other failpoint runtime tests use this plugin to simulate shim task API failures deterministically.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/plugin_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/loopback-v2/main.go -->
# sources/cloud-native/containerd/integration/failpoint/cmd/loopback-v2/main.go

## Purpose

This helper binary checks whether the loopback interface is up inside a container. It supports issue 10244 integration coverage for CNI loopback behavior.

## Important APIs, Types, And Functions

- `isLoInterfaceUp` uses netlink to find interface `lo` and test the `net.FlagUp` bit.
- `main` logs fatal errors and prints `Loopback interface is UP` or `DOWN`.

## Control Flow

The binary resolves `lo` with `netlink.LinkByName`, checks the link flags, and prints a single status line. Any lookup/check failure exits through `log.Fatalf`.

## State And Persistence Behavior

It is read-only. It observes network namespace interface state in the process namespace and does not persist anything.

## Dependencies And Integration Points

It depends on `github.com/vishvananda/netlink` and is mounted into test containers by `issue10244_loopback_linux_test.go`.

## Risks And Edge Cases

The binary must be built and available at `/usr/local/bin/loopback-v2` on the host running the test. It assumes the loopback interface is named `lo`, which is standard for Linux network namespaces.

## Test Signals

When the integration test execs this binary, output containing `UP` confirms loopback setup is correct.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/loopback-v2/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/delayexec.go -->
# sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/delayexec.go

## Purpose

This Linux failpoint profile delays runc `exec` invocations until test-controlled FIFOs signal continuation. It allows integration tests to reproduce races around exec and container lifecycle operations.

## Important APIs, Types, And Functions

- `delayExec` wraps an `invoker` and only delays commands whose argv contains `exec`.
- `delay` triggers a ready FIFO and waits on a delay FIFO.
- `fifoFromProcessEnv` reads FIFO names from the exec process spec environment.
- `processEnvironment` locates `--process <file>`, reads the OCI process JSON, and returns environment variables.
- Environment keys come from `integration/failpoint/const.go`.

## Control Flow

For non-exec runc commands, `delayExec` directly invokes the underlying runc. For exec commands, it parses the process spec to find `_RUNC_FP_DELAY_EXEC_READY` and `_RUNC_FP_DELAY_EXEC_DELAY`, creates a trigger and waiter, signals readiness to the test, blocks until the test releases the delay FIFO, and then calls real runc.

## State And Persistence Behavior

State is externalized through named FIFOs supplied in the process environment. No durable repository or containerd state is written by this file.

## Dependencies And Integration Points

It integrates with the `runc-fp` main wrapper, OCI process JSON, containerd `fifosync`, logrus, and the failpoint environment constants.

## Risks And Edge Cases

The code assumes runc command-line arguments include `--process` for exec. Missing env vars or FIFO creation failures abort the runc command. Environment parsing keeps the last value for duplicate keys.

## Test Signals

Tests using the `delayExec` profile can assert ordering by waiting for the ready FIFO before triggering the delayed runc exec.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/delayexec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/issue9103.go -->
# sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/issue9103.go

## Purpose

This Linux failpoint profile reproduces issue 9103 by killing the runc init process immediately after a successful `runc create`. It forces shim cleanup paths to handle an init process that dies at a sensitive lifecycle point.

## Important APIs, Types, And Functions

- `issue9103KillInitAfterCreate` is an `invokerInterceptor` registered under profile name `issue9103`.
- It reads `init.pid`, parses the PID, sends `SIGKILL`, and sleeps for three seconds.

## Control Flow

The interceptor detects whether the current runc command line contains `create`, invokes real runc first, and returns immediately for non-create commands. For create, it reads the generated `init.pid`, validates it is positive, sends `SIGKILL` to that process, then sleeps to give the shim time to receive `SIGCHLD` and begin cleanup.

## State And Persistence Behavior

It reads the bundle-local `init.pid` file created by runc and mutates process state by killing the init process. No file state is intentionally written.

## Dependencies And Integration Points

It integrates with the `runc-fp` wrapper, runc bundle layout, Linux signals, and shim lifecycle cleanup behavior.

## Risks And Edge Cases

The profile assumes `init.pid` exists after `runc create` and contains a valid integer. The fixed three-second sleep is timing-sensitive but intentionally gives shim cleanup a deterministic window.

## Test Signals

Issue-specific tests using this profile can verify containerd handles init death after create without leaking shim/task state.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/issue9103.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/main.go -->
# sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/main.go

## Purpose

This Linux executable wraps `runc` and dispatches failpoint profiles selected by OCI annotations. It lets tests inject lifecycle faults while still running real runc with the original arguments.

## Important APIs, Types, And Functions

- `failpointProfileKey` is `oci.runc.failpoint.profile`.
- `invoker` and `invokerInterceptor` define wrapper call signatures.
- `failpointProfiles` registers `issue9103` and `delayExec`.
- `setupLog` redirects logrus JSON output to the `--log` file supplied by containerd/go-runc.
- `defaultRuncInvoker` execs `runc` with original arguments and `Pdeathsig=SIGKILL`.
- `failpointProfileFromOCIAnnotation` reads `config.json` and chooses a profile.

## Control Flow

`main` initializes logging, loads the profile from OCI annotations, and invokes it with `defaultRuncInvoker`. The default invoker delegates to the real `runc` binary with `os.Args[1:]`, so profile code can run before/after or around specific runc commands.

## State And Persistence Behavior

The wrapper reads bundle `config.json` and appends logs to the runc log file. It does not persist profile state itself; profiles may coordinate through FIFOs or process signals.

## Dependencies And Integration Points

It integrates with containerd/go-runc command conventions, OCI spec annotations, logrus JSON logs, and Linux process death signal behavior.

## Risks And Edge Cases

The wrapper requires `--log` and a valid profile annotation; missing either is fatal. It assumes `runc` is available in `PATH`. A profile mismatch prevents container startup.

## Test Signals

Successful failpoint tests prove the wrapper can transparently delegate normal runc behavior while applying selected fault injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/const.go -->
# sources/cloud-native/containerd/integration/failpoint/const.go

## Purpose

This package defines shared environment variable names used by failpoint-enabled runc exec delay tests. It keeps the test code and `runc-fp` helper binary aligned.

## Important APIs, Types, And Functions

- `DelayExecReadyEnv` names the FIFO path env var used by `runc-fp` to signal that an exec reached the delay point.
- `DelayExecDelayEnv` names the FIFO path env var used by tests to release the delayed exec.

## Control Flow

The file is declarative and contains no runtime control flow.

## State And Persistence Behavior

The constants describe process environment state. They do not persist data.

## Dependencies And Integration Points

They are consumed by `failpoint/cmd/runc-fp/delayexec.go` and by tests that populate exec process environments with FIFO paths.

## Risks And Edge Cases

Renaming either constant without updating all producers/consumers would break delay-exec coordination. The leading underscore convention reduces collision risk but does not prevent user-specified environment conflicts.

## Test Signals

Tests that exercise delayed runc exec implicitly validate these constants by successfully synchronizing through the expected FIFOs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/failpoint/const.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/image_load_test.go -->
# sources/cloud-native/containerd/integration/image_load_test.go

## Purpose

This test verifies that an image saved as a tarball and imported directly into containerd's `k8s.io` namespace becomes visible to CRI and can be used to create a container.

## Important APIs, Types, And Functions

- `TestImageLoad` is the only test.
- External tools `docker` and `ctr` pull/save/import the image.
- `imageService.ImageStatus`, `imageService.RemoveImage`, and CRI runtime calls validate import visibility and usability.

## Control Flow

The test skips a known Windows Server 2025 host issue. It checks `docker` availability, pulls and saves BusyBox to a temporary tar, removes any existing CRI image, locates `ctr`, imports the tar into the configured containerd endpoint and `k8s.io` namespace using `--local=true` and a platform selector, then waits for CRI `ImageStatus` to see the image. Finally it creates and starts a container from that image and checks it is running.

## State And Persistence Behavior

The test mutates containerd image store state by importing a tarball. Temporary tarball state lives under `t.TempDir`. Container and sandbox state are cleaned up by shared helpers.

## Dependencies And Integration Points

It depends on Docker, `ctr`, containerd endpoint flags, platform-specific image manifests, CRI image reconciliation, and the test BusyBox image.

## Risks And Edge Cases

External CLI availability is a major host dependency. Docker image store behavior can save multi-platform artifacts, so the platform flag avoids missing manifest references. CRI visibility is asynchronous and requires polling.

## Test Signals

Passing confirms directly imported images are indexed by CRI and runnable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/image_load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/image_pull_timeout_test.go -->
# sources/cloud-native/containerd/integration/image_pull_timeout_test.go

## Purpose

This Linux test suite validates CRI image pull progress timeout behavior for local pull and transfer-service paths. It distinguishes true network inactivity from benign waits such as slow content commit or singleflight waits on already-open content writers.

## Important APIs, Types, And Functions

- `TestCRIImagePullTimeout` runs six subtests across three scenarios and two pull implementations.
- `testCRIImagePullTimeoutBySlowCommitWriter` uses `tweakContentInitFnWithDelayer` to delay content commit.
- `testCRIImagePullTimeoutByHoldingContentOpenWriter` opens content writers for manifest descriptors to simulate singleflight waiters.
- `testCRIImagePullTimeoutByNoDataTransferred` uses a local mirror registry with a circuit-breaking copy limiter.
- `mirrorRegistryServer`, `ioCopyLimiter`, and `limitedCopy` implement the throttling HTTP proxy.
- `initLocalCRIImageService` constructs a CRI image service over a local containerd client.

## Control Flow

The suite runs only on Linux and in parallel. Slow-commit tests build a local containerd client with a delayed content store and expect pull success despite commit taking longer than the progress timeout. Holding-writer tests lock manifest descriptors, start a pull, ensure it does not return while blocked, release writers after multiple timeouts, and expect success. No-data-transferred tests configure a mirror that forwards to GHCR but sleeps after sending 3 MiB; CRI should cancel the pull with `context.Canceled` and the test cleans up the lease synchronously.

## State And Persistence Behavior

State is isolated in temporary containerd roots, content stores, leases, host registry config files, and httptest mirror state. `ioCopyLimiter.hitCircuitBreaker` records whether the simulated stall occurred.

## Dependencies And Integration Points

It integrates CRI image service internals, containerd content/lease APIs, registry mirror configuration, transfer service versus local pull behavior, HTTP auth header rewriting, and GHCR-hosted `volume-ownership:2.1`.

## Risks And Edge Cases

The tests depend on external network access to GHCR except for the local proxy layer. Parallel pulls can be resource-heavy. The mirror rewrites auth headers and assumes GHCR response shapes. Lease cleanup is required to remove failed pull content.

## Test Signals

Passing confirms CRI progress timeout cancels truly stalled network transfers but not commit delays or singleflight/content-lock waits.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/image_pull_timeout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/image_volume_linux_test.go -->
# sources/cloud-native/containerd/integration/image_volume_linux_test.go

## Purpose

This Linux file validates CRI image volume mounts: read-only behavior, SELinux relabeling, subpath validation, snapshot cleanup, volatile overlay options, restart/idempotency behavior, and user namespace idmapped image volume ownership.

## Important APIs, Types, And Functions

- `TestImageVolumeBasic` table-tests read-only content, SELinux levels, subpath success, and rejected unsafe subpaths.
- `setupRunningContainerWithImageVolume` creates a pod/container with `WithImageVolumeMount`.
- `TestImageVolumeCheckVolatileOption` inspects overlay mount options for `volatile` or `fsync=volatile`.
- `TestImageVolumeSetupIfContainerdRestarts` verifies preexisting snapshot state is reused and not double-mounted.
- `TestImageVolumeWithUserNamespace` checks idmapped read-only image volume behavior.

## Control Flow

The basic test creates containers with image-volume mounts, optionally skips SELinux cases, verifies snapshot mounts exist, executes commands inside the container, and after pod cleanup polls until the image volume snapshot is gone. Subpath cases expect create errors for single-file, nonexistent, absolute, escaping, or symlink-escaping paths. The volatile test locates the image volume mount and inspects VFS options. The restart/idempotency test pre-creates snapshot targets before container creation and ensures multiple containers share the same mount. The user namespace test gates on userns, pidfd, and idmap support, then verifies access, read-only enforcement, and root ownership inside the namespace.

## State And Persistence Behavior

The tests create image volume snapshots under pod image volume directories and verify cleanup after pod deletion. They also observe mount table state and containerd overlay snapshotter metadata.

## Dependencies And Integration Points

They integrate CRI image volume mount fields, overlayfs snapshotter, containerd snapshot service, SELinux, kernel idmap support, pidfd support, and images `Alpine`, `Pause`, and `ResourceConsumer`.

## Risks And Edge Cases

Host kernel, SELinux, overlayfs, and idmap capabilities strongly affect coverage. The file contains the namespace label `"image-voloume"` typo only as a test namespace string. Cleanup polling can be slow if snapshot garbage collection stalls.

## Test Signals

Passing shows image volumes are mounted safely, read-only, labeled/idmapped correctly, not double-mounted, and cleaned up.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/image_volume_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/imagefs_info_test.go -->
# sources/cloud-native/containerd/integration/imagefs_info_test.go

## Purpose

This test verifies CRI `ImageFsInfo` reports a populated filesystem usage record once images and snapshots exist.

## Important APIs, Types, And Functions

- `TestImageFSInfo` is the only test.
- `imageService.ImageFsInfo` retrieves filesystem usage.
- `EnsureImageExists` and `PodSandboxConfigWithCleanup` create data for imagefs accounting.

## Control Flow

The test creates a sandbox to ensure an active snapshot, pulls BusyBox to make image storage non-empty, then polls `ImageFsInfo` until exactly one usage entry exists with nonzero timestamp, nonzero used bytes, and a non-empty mountpoint. It then verifies that the reported mountpoint exists on the host filesystem.

## State And Persistence Behavior

The state observed is image filesystem accounting derived from containerd image/snapshot storage. The test persists no custom data beyond normal pulled image and sandbox state.

## Dependencies And Integration Points

It integrates with CRI image service stats collection, snapshotter filesystem paths, host `os.Stat`, and the shared polling helper.

## Risks And Edge Cases

Stats collection is asynchronous and may lag, so the test polls for up to 30 seconds. Environments with multiple image filesystems would fail because the test expects fewer than two entries.

## Test Signals

Passing confirms CRI reports image filesystem usage with a real mountpoint after image/snapshot activity.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/imagefs_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/image_list.go -->
# sources/cloud-native/containerd/integration/images/image_list.go

## Purpose

This package centralizes public image references used by containerd integration tests and allows overriding them from a TOML file. It provides stable integer constants and a `Get` accessor for test code.

## Important APIs, Types, And Functions

- `imageListFile` defines the `-image-list` flag.
- `ImageList` contains named image reference fields.
- `initImages` sets defaults, optionally loads TOML overrides, logs the list, and initializes `imageMap`.
- Constants `Alpine`, `BusyBox`, `Pause`, `ResourceConsumer`, `VolumeCopyUp`, `VolumeOwnership`, `ArgsEscaped`, `Nginx`, and `Whiteout` index the map.
- `Get` lazily initializes once and returns a reference by constant.

## Control Flow

The first `Get` call triggers `initOnce.Do`. Defaults are assigned, optional TOML content is read and unmarshaled over the struct, and `initImageMap` maps constants to struct fields. Later calls reuse the initialized map.

## State And Persistence Behavior

Package-level `imageList`, `imageMap`, and `initOnce` hold process-local state. No files are written. The TOML override file is read once and later changes are ignored.

## Dependencies And Integration Points

It integrates with Go flags parsed in test startup, containerd logging, and `pelletier/go-toml/v2`. Almost every integration test imports this package for image references.

## Risks And Edge Cases

Unknown integer constants return the zero map value. TOML key casing must match decoder behavior; the sample mixes lower-case and exported field names. Read/unmarshal failures panic because tests cannot proceed safely with an invalid image list.

## Test Signals

Indirect test signal is broad: successful image pulls across the integration suite validate that defaults or overrides are valid.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/image_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/image_list.sample.toml -->
# sources/cloud-native/containerd/integration/images/image_list.sample.toml

## Purpose

This sample TOML file documents how to override integration test image references with the `-image-list` flag.

## Important APIs, Types, And Functions

- Keys correspond to fields in `images.ImageList`: `alpine`, `busybox`, `pause`, `VolumeCopyUp`, `VolumeOwnership`, and `ArgsEscaped`.
- Values are fully qualified image references used by integration tests.

## Control Flow

The file has no executable control flow. It is consumed by `image_list.go` when a test process is started with `-image-list=<path>`.

## State And Persistence Behavior

It is static configuration. When copied and passed to tests, it affects process-local image map initialization only.

## Dependencies And Integration Points

It integrates with TOML unmarshalling in `initImages` and with test image pull behavior throughout the integration suite.

## Risks And Edge Cases

The sample uses mixed key casing; override authors should verify TOML decoding maps keys to intended exported fields. The `VolumeCopyUp` sample version is `2.1`, while the current default in code is `2.2`, so copying it verbatim may intentionally or accidentally test an older fixture.

## Test Signals

Tests started with this sample should pull Docker Hub BusyBox/Alpine and the listed containerd fixture images instead of hard-coded defaults.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/image_list.sample.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-copy-up/Dockerfile -->
# sources/cloud-native/containerd/integration/images/volume-copy-up/Dockerfile

## Purpose

This fixture image defines image volumes with preexisting files to test volume copy-up behavior, including Linux handling of paths that resemble Windows drive-letter paths or contain colons.

## Important APIs, Types, And Functions

- `ARG BASE` selects an OS/architecture-specific base image from the Makefile.
- `RUN` commands create `/test_dir/test_file`, `/C:/weird_test_dir/weird_test_file`, and `/:colon_prefixed/colon_prefixed_file`.
- `VOLUME` declares `/test_dir`, `C:/weird_test_dir`, and `/:colon_prefixed`.

## Control Flow

At image build time, the Dockerfile creates directories and files, then marks them as image-defined volumes. At runtime, CRI volume copy-up logic should populate host volume directories with those contents.

## State And Persistence Behavior

The built image persists the declared volumes and initial file contents in image metadata/layers. Tests later validate host volume state and container-visible contents.

## Dependencies And Integration Points

It is built by the sibling Makefile and consumed by user namespace volume copy-up tests. It deliberately includes path forms that interact with Windows path normalization logic.

## Risks And Edge Cases

The Linux Dockerfile comments explain that Windows treats drive-letter paths specially, while Linux must not mangle them. Changing volume paths can invalidate tests expecting exactly three Linux volumes.

## Test Signals

`TestUsernsVolumeCopyUp` checks that these declared volumes are copied up and have correct contents/ownership in a user namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-copy-up/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-copy-up/Makefile -->
# sources/cloud-native/containerd/integration/images/volume-copy-up/Makefile

## Purpose

This Makefile builds and publishes multi-architecture `ghcr.io/containerd/volume-copy-up:2.2` fixture images for Linux and optionally Windows. The fixture supports CRI volume copy-up integration tests.

## Important APIs, Types, And Functions

- Variables `PROJ`, `VERSION`, `IMAGE`, `OS`, `ARCH`, `OSVERSION`, and `OUTPUT_TYPE` parameterize builds.
- `build`, `build-local`, `build-registry`, `container`, and `push-manifest` are primary targets.
- Pattern target `sub-container-%` decomposes output/OS/arch/version tokens.
- `.container-linux-*` uses `docker buildx build`.
- `.container-windows-*` uses remote Docker arguments and `Dockerfile_windows`.

## Control Flow

`make build` selects buildx and builds all Linux architectures into the local Docker output. `make push` configures registry auth, builds registry outputs for all enabled OS/arch combinations, and pushes a manifest list. Windows builds are enabled only when `REMOTE_DOCKER_URL` is set and include OS version annotations in the final manifest.

## State And Persistence Behavior

The Makefile creates local Docker/buildx images or registry images and manifests. It does not manage source-tree state.

## Dependencies And Integration Points

It depends on Docker/buildx, optional gcloud auth, optional remote Windows Docker, and the Dockerfiles in the fixture directory. Integration tests reference the published image through `images.VolumeCopyUp`.

## Risks And Edge Cases

Manifest annotation relies on parsing `docker manifest inspect` output with grep/awk. Remote Windows builds require certificates and Hyper-V isolation. Local builds only cover Linux targets.

## Test Signals

The downstream test signal is that the published image contains the expected volume declarations and copied contents for volume-copy-up tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-copy-up/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-ownership/Dockerfile -->
# sources/cloud-native/containerd/integration/images/volume-ownership/Dockerfile

## Purpose

This fixture image defines a volume directory owned by `nobody:nogroup`, used to test image-defined volume ownership and overlay volatile behavior.

## Important APIs, Types, And Functions

- `FROM ubuntu` provides the base.
- A `RUN` command creates `/test_dir` and changes ownership to `nobody:nogroup`.
- `VOLUME /test_dir` declares the image volume.

## Control Flow

At build time, the image creates and changes ownership of `/test_dir`. At runtime, CRI image-defined volume handling should create/mount a volume using this metadata.

## State And Persistence Behavior

The image layer persists directory ownership and the config persists the volume declaration. No runtime state is managed in the Dockerfile.

## Dependencies And Integration Points

It is built by the sibling Makefile and used by `container_volume_linux_test.go`, image pull timeout tests, and image fixture references in `image_list.go`.

## Risks And Edge Cases

The image assumes Ubuntu contains `nobody:nogroup`. Changing the volume path breaks tests that refer to `/test_dir` or the published fixture semantics.

## Test Signals

Tests using `images.VolumeOwnership` validate that containerd can pull/run the image and handle its volume declaration under specific snapshotter settings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-ownership/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-ownership/Makefile -->
# sources/cloud-native/containerd/integration/images/volume-ownership/Makefile

## Purpose

This Makefile builds and publishes multi-architecture `ghcr.io/containerd/volume-ownership:2.1` fixture images for Linux and optionally Windows. The fixture supports ownership, image pull timeout, and volume behavior tests.

## Important APIs, Types, And Functions

- Build variables mirror the volume-copy-up Makefile: `PROJ`, `VERSION`, `IMAGE`, `OS`, `ARCH`, `OSVERSION`, and `OUTPUT_TYPE`.
- `build-tools` compiles `tools/get_owner_windows.go` for Windows image builds.
- `clean-tools` removes the generated helper executable.
- `build`, `push`, `build-local`, `build-registry`, `container`, and `push-manifest` orchestrate image creation.

## Control Flow

Linux local builds use buildx for all Linux architectures. Registry builds compile the Windows owner helper first, build all enabled Linux and Windows images, clean the helper, then create/push a manifest list. Windows builds are enabled when `REMOTE_DOCKER_URL` is set.

## State And Persistence Behavior

It creates Docker/buildx images, optional helper binaries, and registry manifests. The generated Windows helper is cleaned after registry builds.

## Dependencies And Integration Points

It depends on Docker/buildx, Go for the Windows helper, optional gcloud auth, optional remote Windows Docker, and Dockerfiles in the fixture directory. Integration tests reference the published image by default.

## Risks And Edge Cases

The Windows helper build uses `-mod=vendor`, so vendor state matters. Manifest OS version annotation uses shell parsing. Failed builds can leave `tools/get_owner_windows.exe` until `clean-tools` runs.

## Test Signals

Downstream tests validate this image by pulling it, using it for image pull timeout traffic, and running containers with image-defined volumes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-ownership/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-ownership/tools/get_owner_windows.go -->
# sources/cloud-native/containerd/integration/images/volume-ownership/tools/get_owner_windows.go

## Purpose

This Windows helper prints the owner account and SID for a file or directory. It is built into Windows volume-ownership fixture images to support ownership validation.

## Important APIs, Types, And Functions

- `main` validates it received one path argument, checks the path exists, reads security information, resolves the owner SID to an account, and prints `account:sid`.
- `windows.GetNamedSecurityInfo` retrieves owner and DACL information.
- `sid.LookupAccount(".")` resolves the SID locally.

## Control Flow

The program exits with usage text if the argument count is wrong. It `Stat`s the target, fetches Windows file security info, obtains the owner SID, resolves it, and prints a compact result. Errors are fatal through `log.Fatal`.

## State And Persistence Behavior

The helper is read-only. It inspects filesystem ACL/owner metadata and writes only stdout/stderr.

## Dependencies And Integration Points

It depends on `golang.org/x/sys/windows` and is compiled by the volume-ownership Makefile for Windows fixture images.

## Risks And Edge Cases

It is Windows-only by API usage even though there is no build tag. Building it for non-Windows would fail; the Makefile explicitly sets `GOOS=windows`. Account lookup can fail for unresolvable SIDs.

## Test Signals

Windows volume ownership tests can execute this helper and compare the printed owner information.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/images/volume-ownership/tools/get_owner_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue10244_loopback_linux_test.go -->
# sources/cloud-native/containerd/integration/issue10244_loopback_linux_test.go

## Purpose

This Linux regression test validates that the loopback interface is up inside pods regardless of the CRI CNI `use_internal_loopback` setting. It covers issue 10244 behavior around loopback setup.

## Important APIs, Types, And Functions

- `TestIssue10244LoopbackV2` table-tests `use_internal_loopback=false` and `true`.
- `checkLoopbackResult` writes an isolated containerd config, starts containerd, runs a test container, and executes the loopback helper.

## Control Flow

For each setting, the test writes `config.toml` with the CRI runtime CNI option, starts a new containerd process, registers cleanup, pulls BusyBox, creates a pod/container with `/usr/local/bin/loopback-v2` bind-mounted into the container, runs the helper through `ExecSync`, and asserts stdout contains `UP`.

## State And Persistence Behavior

It creates an isolated temporary containerd work directory and config file. Pods and the containerd process are cleaned up after each subtest.

## Dependencies And Integration Points

It integrates with containerd process management helpers, CRI CNI configuration, the `loopback-v2` helper binary, host bind mounts, and BusyBox.

## Risks And Edge Cases

The helper binary must exist at `/usr/local/bin/loopback-v2`. The config uses the CRI v1 runtime plugin path and assumes the isolated containerd can start with defaults for all other settings.

## Test Signals

Passing confirms pod network namespaces have an operational loopback interface with both internal and external loopback handling paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue10244_loopback_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue10467_linux_test.go -->
# sources/cloud-native/containerd/integration/issue10467_linux_test.go

## Purpose

This Linux upgrade regression test verifies migration of sandbox metadata from an old incorrect root bucket layout into the proper namespace bucket layout. It reproduces state from containerd v1.7.20 and validates current migration.

## Important APIs, Types, And Functions

- `TestIssue10467` is the only test.
- External helpers `downloadReleaseBinary`, `oneSevenCtrdConfig`, `currentReleaseCtrdDefaultConfig`, and `shouldManipulateContainersInPodAfterUpgrade` prepare and verify upgrade scenarios.
- `bbolt.Open` inspects `meta.db` buckets before and after migration.

## Control Flow

The test downloads v1.7.20, starts that containerd with `ENABLE_CRI_SANDBOXES=yes`, creates pods/containers through an upgrade case helper, stops the old process, and opens the bolt metadata database to assert a root `k8s.io` bucket exists. It then writes current config, starts current containerd on the same work directory, copies `meta.db`, asserts the root `k8s.io` bucket no longer exists, and runs the upgrade verification function against the migrated state.

## State And Persistence Behavior

The central persisted state is containerd's bolt metadata database under the temporary root. The test intentionally creates old-format metadata and verifies current startup migrates it.

## Dependencies And Integration Points

It depends on release binary download, old/current containerd config helpers, CRI runtime/image services, `go.etcd.io/bbolt`, and continuity file copying.

## Risks And Edge Cases

Network or release availability can break setup. The test assumes v1.7.20 preserves the old bucket shape. Direct bolt inspection is tightly coupled to metadata schema.

## Test Signals

Passing confirms current containerd migrates old sandbox metadata and existing pods/containers remain usable after upgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue10467_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue7496_linux_test.go -->
# sources/cloud-native/containerd/integration/issue7496_linux_test.go

## Purpose

This Linux regression test reproduces issue 7496/8931, where slow `umount2` during sandbox deletion could leak shims or block cleanup. It injects syscall delay with `strace` and verifies pod removal eventually succeeds and the shim exits.

## Important APIs, Types, And Functions

- `TestIssue7496` orchestrates the reproduction.
- `injectDelayToUmount2` attaches `strace` to a shim PID and injects delay into `umount2`.
- `connectToShim` resolves the shim socket and creates a ttrpc task client.
- `shimPid` calls shim `Connect` to get the shim process ID.

## Control Flow

The test creates a sandbox, connects to its shim, attaches `strace` with a 12-second `umount2` delay, creates and starts a container, then loops `StopPodSandbox` and `RemovePodSandbox` until they succeed or a three-minute context expires. After deletion, it waits for `strace` to exit. If `strace` is still running after 15 seconds, it expects shim connection failure, logs an error, kills the shim, and drains the strace goroutine.

## State And Persistence Behavior

The test mutates live shim process behavior through `strace` and observes sandbox/container runtime state. It does not write durable state except normal containerd metadata during the test.

## Dependencies And Integration Points

It depends on Linux `strace` with syscall injection support, shim ttrpc APIs, Unix sockets, CRI sandbox/container deletion, and Pause image availability.

## Risks And Edge Cases

The test is host-tool and timing sensitive. `strace` must be installed and new enough. Attaching to shims may require privileges. The cleanup path kills leaked shims only after a failure condition.

## Test Signals

Passing means sandbox removal tolerates slow unmounts and does not leave the shim stuck under the injected delay.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue7496_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue7496_shutdown_linux_test.go -->
# sources/cloud-native/containerd/integration/issue7496_shutdown_linux_test.go

## Purpose

This Linux regression test documents a desired retry behavior for shim `Shutdown` after issue 7496-style timing races. It is currently skipped until retry support is available.

## Important APIs, Types, And Functions

- `TestIssue7496_ShouldRetryShutdown` is the skipped test.
- `injectShimFailpoint` is called to inject a `Shutdown` failpoint into the sandbox config.
- `connectToShim` and `shimPid` inspect the failpoint-enabled shim.

## Control Flow

If enabled, the test would create a sandbox using the failpoint runtime handler with a `Shutdown` failpoint that returns one error, connect to its shim, stop and remove the sandbox, and then assert that connecting to the shim fails, proving it was eventually shut down despite the injected error.

## State And Persistence Behavior

The intended state under test is shim lifecycle after a transient shutdown API failure. Failpoint configuration is carried through sandbox annotations into the failpoint shim.

## Dependencies And Integration Points

It depends on the failpoint shim runtime, ttrpc task APIs, CRI sandbox lifecycle, and the `injectShimFailpoint` helper defined elsewhere in the integration suite.

## Risks And Edge Cases

The test is explicitly skipped with a message to re-enable when shutdown retry is implemented. If enabled prematurely, it would fail by design.

## Test Signals

Currently the only signal is skipped coverage. When re-enabled, passing would confirm transient shim shutdown errors are retried rather than leaking the shim.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/issue7496_shutdown_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/main_test.go -->
# sources/cloud-native/containerd/integration/main_test.go

## Purpose

This file is the shared integration test harness for containerd CRI tests. It initializes global CRI/containerd clients, defines pod/container config builders, polling utilities, process helpers, raw gRPC access, config/status helpers, restart logic, and image-pull helpers used throughout the integration package.

## Important APIs, Types, And Functions

- `TestMain`, `ConnectDaemons`, and `DisconnectDaemons` manage global `runtimeService`, `runtimeService2`, `imageService`, and `containerdClient`.
- `PodSandboxOpts`, `PodSandboxConfig`, `PodSandboxConfigWithCleanup`, and many `With...` pod options build CRI sandbox configs.
- `ContainerOpts`, `ContainerConfig`, and many `With...` container options build CRI container configs.
- `Eventually` and `Consistently` provide polling assertions.
- Process helpers include `KillProcess`, `KillPid`, `PidOf`, `PidsOf`, and `PidEnvs`.
- `RawRuntimeClient`, `CRIConfig`, `SandboxInfo`, `RestartContainerd`, `EnsureImageExists`, and `GetContainer` expose lower-level integration access.

## Control Flow

`TestMain` parses flags, connects to CRI runtime/image services and containerd, runs tests, then disconnects. Config builders initialize required nested CRI protobuf fields lazily and apply option functions. Polling helpers loop until success, error, or timeout. Restart logic kills containerd by process name, waits for it to exit, then repeatedly reconnects global clients. `CRIConfig` and `SandboxInfo` call verbose CRI status APIs and unmarshal JSON info.

## State And Persistence Behavior

The file owns process-global clients and endpoint state. It creates randomized pod namespaces with generated IDs. Cleanup is registered through `testing.T.Cleanup` for sandboxes and containers. It reads current CRI config/status and process `/proc` state but writes no durable repository files.

## Dependencies And Integration Points

It integrates with containerd client APIs, CRI remote services, gRPC, Kubernetes CRI client dialers, SELinux, containerd CRI config/types, image package flag parsing, OS process utilities, and platform-specific process commands.

## Risks And Edge Cases

Global clients mean restart tests must carefully reconnect and avoid parallel interference. Many helpers assume Linux `/proc`, Unix sockets, or specific process names, with some Windows branches. `Eventually` returns immediately on any error, so callers must decide whether transient errors are retryable.

## Test Signals

Nearly every integration test depends on this harness; broad suite success validates its config construction, cleanup, polling, client connection, and image-pull behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/no_metadata_test.go -->
# sources/cloud-native/containerd/integration/no_metadata_test.go

## Purpose

This file verifies that invalid CRI requests missing required metadata fail gracefully and do not break runtime service health.

## Important APIs, Types, And Functions

- `TestRunPodSandboxWithoutMetadata` calls `RunPodSandbox` with an empty `PodSandboxConfig`.
- `TestCreateContainerWithoutMetadata` calls `CreateContainer` with an empty `ContainerConfig`.
- `runtimeService.Status` checks service health after each expected error.

## Control Flow

The sandbox test submits an empty config and requires an error, then requires `Status` to succeed. The container test creates a valid sandbox, submits an empty container config against it, requires an error, and again checks `Status`.

## State And Persistence Behavior

The invalid requests should not persist sandbox/container metadata. The valid sandbox in the second test is cleaned up through `PodSandboxConfigWithCleanup`.

## Dependencies And Integration Points

It integrates with CRI validation paths for required metadata and the runtime status endpoint.

## Risks And Edge Cases

The tests only assert that an error occurs, not a specific validation code/message. They validate service survival but not absence of partial metadata records.

## Test Signals

Passing means malformed metadata requests are rejected without making the CRI plugin unhealthy.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/no_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/nri_linux_test.go -->
# sources/cloud-native/containerd/integration/nri_linux_test.go

## Purpose

This Linux file validates that NRI plugins receive correct pod networking attributes during synchronization and lifecycle events. It compares NRI-reported pod IPs and network namespace paths against live netlink inspection.

## Important APIs, Types, And Functions

- `TestNriPluginNetworkingSynchronization` creates multiple pods/containers before connecting a plugin and validates synchronized network data.
- `TestNriPluginNetworkingLifecycle` validates `RunPodSandbox`, `StopPodSandbox`, and `RemovePodSandbox` networking data.
- `getNetworkNamespace` extracts the network namespace path from an NRI pod.
- `getNetworkNamespaceIPs` opens the namespace and lists global unicast addresses on `eth0`.

## Control Flow

Both tests skip when NRI is unavailable. The synchronization test creates three pods with two containers each, connects a mock plugin with a custom `synchronize` hook, filters pods by test prefix, and checks NRI IPs match netlink-discovered IPs. It also verifies all test pods and containers are present in plugin state. The lifecycle test connects a plugin with custom pod hooks, creates/stops/removes one pod, waits for events, and checks network namespace/IP semantics at each stage; removal should keep assigned IPs but no longer have a namespace path.

## State And Persistence Behavior

Plugin state is kept in `mockPlugin.pods`, `mockPlugin.ctrs`, and event queues from `nri_test.go`. Network namespace state is live kernel state, not persisted by the test.

## Dependencies And Integration Points

It integrates with containerd NRI APIs, the local mock plugin framework, CRI pod/container lifecycle, `vishvananda/netns`, `vishvananda/netlink`, and CNI-created `eth0`.

## Risks And Edge Cases

The tests assume pod interfaces are named `eth0` and use global unicast addresses. Network namespace access can fail due to permissions or timing. Hook synchronization uses channels and short timeouts.

## Test Signals

Passing confirms NRI synchronization/lifecycle payloads include accurate network namespace and IP information.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/nri_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/nri_test.go -->
# sources/cloud-native/containerd/integration/nri_test.go

## Purpose

This file provides the main NRI integration suite and mock plugin framework. It tests plugin setup, synchronization, container adjustments, resource updates, pod sandbox updates, restart behavior, and event recording.

## Important APIs, Types, And Functions

- `skipNriTestIfNecessary` gates Linux, SELinux, socket, and extra resource checks.
- Tests cover plugin setup/sync, mount/env/annotation/device injection, cpuset/memset adjustments and updates, pod resource updates, persistence across containerd restart, and plugin connection closure on restart.
- `nriTest` manages per-test namespace, pods, containers, runtime service, and plugins.
- `mockPlugin` implements NRI stub callbacks and stores pods/containers/events.
- `Event`, `eventQ`, and helper constructors provide event matching and waiting.
- `getAvailableCpuset`, `getAvailableMemset`, and `getXxxset` parse host CPU/NUMA sets.

## Control Flow

Each test sets up `nriTest`, optionally installs customized callback functions on a `mockPlugin`, starts plugins via `stub.New`, then creates pods/containers with CRI. Adjustment tests inject mounts, environment variables, annotations, devices, or cpuset/memset changes during `CreateContainer` and verify effects from inside the container or plugin state. Update tests return `ContainerUpdate` objects for existing containers and check observed cgroup-visible status files. Pod update tests call `UpdatePodSandboxResources` and wait for update/post-update events. Restart tests call `RestartContainerd` and verify resource persistence or closed plugin connections.

## State And Persistence Behavior

The mock plugin stores synchronized pod/container snapshots and an in-memory event queue. Pod sandbox resource updates are persisted in CRI sandbox info and verified after containerd restart. Temporary output directories capture container-observed effects.

## Dependencies And Integration Points

The file integrates with containerd NRI `api` and `stub`, CRI runtime APIs, BusyBox containers, SELinux detection, `/sys` CPU/NUMA files, and the shared restart and sandbox-info helpers.

## Risks And Edge Cases

NRI tests require a containerd instance with `/var/run/nri-test.sock` enabled and skip under SELinux. Resource-set tests need at least two CPUs or memory nodes. `eventQ` allows only one active waiter. Some shell loops in update tests are timing-sensitive.

## Test Signals

Passing confirms NRI plugin registration, synchronization, callback ordering, container/pod mutation effects, resource update propagation, and restart behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/nri_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/oom_linux_test.go -->
# sources/cloud-native/containerd/integration/oom_linux_test.go

## Purpose

This Linux test stress-validates OOM event monitoring across repeated concurrent container OOMs. It ensures containers killed by memory limits report exit code 137 and reason `OOMKilled`.

## Important APIs, Types, And Functions

- `TestOOMEventMonitor` is the only test.
- It uses `newCtrdProc` to start an isolated containerd binary from `buildDir`.
- `podTCtx.createContainer` starts containers with tight memory and swap limits.
- `Eventually` polls container status for OOM results.

## Control Flow

The test writes a temporary containerd config pointing runc runtime path to the build directory, starts containerd, pulls BusyBox, creates eight host-network pod sandboxes, and then runs ten rounds. In each round it concurrently starts one container per pod executing `dd if=/dev/zero of=/dev/null bs=20M` with 15 MiB memory/swap limits. Each goroutine waits for the container to exit with code 137 and reason `OOMKilled`, then removes it.

## State And Persistence Behavior

State is isolated to the temporary containerd root and repeated container metadata/task records. It deliberately creates OOM events and validates their translation into CRI container status.

## Dependencies And Integration Points

It depends on Linux memory cgroups, built containerd/shim binaries in `buildDir`, BusyBox `dd`, CRI status, and concurrent test helper behavior.

## Risks And Edge Cases

The workload is resource-intensive and timing-sensitive. Hosts without swap accounting or with different OOM behavior could fail. The use of `sync.WaitGroup.Go` requires the Go version/library support present in this source tree.

## Test Signals

Passing indicates containerd consistently monitors and reports OOMKilled events under repeated concurrent pressure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/oom_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/pod_dualstack_test.go -->
# sources/cloud-native/containerd/integration/pod_dualstack_test.go

## Purpose

This test verifies CRI pod network status reports additional IPs only when the container network is actually dual-stack. It compares pod status with network information observed inside the container.

## Important APIs, Types, And Functions

- `TestPodDualStack` is the only test.
- It runs `ip address show dev eth0` on Linux or `ipconfig` on Windows.
- `runtimeService.PodSandboxStatus` provides primary and additional pod IPs.

## Control Flow

The test creates a sandbox with a log directory, runs a short-lived BusyBox container that prints network interface information, waits for exit, reads the container log, and retrieves pod sandbox status. Regexes detect IPv4 and IPv6 global addresses in the log. If both are present, the test requires exactly one additional IP, with the primary IP IPv4 and the additional IP IPv6. Otherwise it requires no additional IPs and a non-empty primary IP.

## State And Persistence Behavior

The test observes live CNI-provided network configuration and CRI pod status. The container log is temporary persisted evidence of in-container network state.

## Dependencies And Integration Points

It integrates CRI pod status networking fields, CNI behavior, platform-specific network commands, regex parsing, and Go `net.ParseIP`.

## Risks And Edge Cases

Regex detection is command-output dependent. The test assumes dual-stack means one primary IPv4 plus one additional IPv6, which matches current CRI expectations but not every possible network policy.

## Test Signals

Passing confirms CRI additional IP reporting matches actual single-stack or dual-stack container network state.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/pod_dualstack_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/pod_hostname_test.go -->
# sources/cloud-native/containerd/integration/pod_hostname_test.go

## Purpose

This test validates pod hostname behavior for regular and host-network pods, including rejection of custom hostnames with host networking.

## Important APIs, Types, And Functions

- `TestPodHostname` table-tests regular custom hostname, host-network default hostname, and host-network custom hostname failure.
- `WithPodHostname`, `WithHostNetwork`, and `WithPodLogDirectory` configure sandbox cases.

## Control Flow

The test gets the host hostname, then for each case creates a sandbox config. Host-network cases skip on Windows. If `RunPodSandbox` errors, the test only accepts that for the expected-error case. Otherwise it starts a BusyBox container that prints `/etc/hostname`, `hostname`, and environment variables, waits for exit, reads the log, and checks `HOSTNAME=` or `COMPUTERNAME=` plus `/etc/hostname=` contain the expected value.

## State And Persistence Behavior

The test observes generated container hostname files and environment variables. Evidence is persisted in the temporary CRI log file.

## Dependencies And Integration Points

It integrates CRI sandbox hostname fields, host network namespace policy, BusyBox shell utilities, Windows environment naming, and log handling.

## Risks And Edge Cases

The Windows branch only applies to non-host-network cases. Host hostnames may contain values requiring exact matching in logs. The failure case asserts only that an error occurs, not a specific validation message.

## Test Signals

Passing confirms hostname propagation and host-network validation behavior are correct.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/pod_hostname_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/pod_userns_linux_test.go -->
# sources/cloud-native/containerd/integration/pod_userns_linux_test.go

## Purpose

This Linux file validates pod/container user namespace support, idmapped host and image volumes, rootfs ownership, host network compatibility, a stdout/stderr permission regression, and volume copy-up behavior in user namespaces.

## Important APIs, Types, And Functions

- `supportsUserNS`, `supportsIDMap`, and `supportsRuncIDMap` gate tests by kernel/filesystem/runtime capability.
- `traversePath` adjusts temporary directory permissions so idmapped volume paths can be traversed.
- `TestPodUserNS` table-tests UID/GID maps, host network, rootfs permissions, idmapped host volumes, and rejection of multiple mappings.
- `TestIssue10598` validates non-root userns init processes can open `/dev/stdout` or `/dev/stderr` using Nginx startup logs.
- `TestUsernsVolumeCopyUp` validates image-defined volume copy-up contents, ownership, and host-path updates under user namespaces.

## Control Flow

Capability helpers check `/proc/self/ns/user`, clone a mount tree and apply `MOUNT_ATTR_IDMAP`, and inspect `runc features`. `TestPodUserNS` creates userns sandbox configs, starts short-lived containers that print maps or stat paths, and checks log output; volume cases pass ID mappings into mounts. `TestIssue10598` starts Nginx in a userns with SELinux options adjusted, then waits for startup logs while ensuring the container remains running. `TestUsernsVolumeCopyUp` starts the volume-copy-up image in a userns, discovers bind volume host paths via helpers from elsewhere, checks copied files and `stat` ownership inside the container, modifies a file inside the container, and verifies the host file changed.

## State And Persistence Behavior

The tests create user namespace mappings in CRI sandbox/container configs, idmapped mounts, temporary host volume directories, and container logs. Volume copy-up creates host-side volume directories populated from image-declared volumes and then mutates one file from inside the container.

## Dependencies And Integration Points

They integrate Linux user namespaces, mount idmapping syscalls, runc feature reporting, CRI user namespace fields, SELinux options, Nginx and volume-copy-up images, host volume mapping helpers, and BusyBox/stat commands.

## Risks And Edge Cases

Coverage is highly host-dependent: kernel, filesystem, runtime, pid/user namespace, and SELinux policy all matter. `traversePath` assumes the temp directory path is under `os.TempDir`. Multiple-mapping behavior is expected to fail but only checks that an error occurs.

## Test Signals

Passing confirms CRI user namespace configuration, idmapped rootfs/volumes, stdio permissions, and volume copy-up behavior work together on capable Linux hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/pod_userns_linux_test.go -->
