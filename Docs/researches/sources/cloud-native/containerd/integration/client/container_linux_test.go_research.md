<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_linux_test.go -->
# sources/cloud-native/containerd/integration/client/container_linux_test.go

## Purpose
Provides Linux-specific integration coverage for task resource updates, shim cgroups, descriptor leaks, daemon restart recovery, direct IO attach, user and user-namespace handling, host PID behavior, runtime options, ambient capabilities, OOM score propagation, and several runc/shim regressions.

## APIs, Types, And Functions
Important tests include `TestTaskUpdate`, `TestShimInCgroup`, `TestShimDoesNotLeakPipes`, `TestShimDoesNotLeakSockets`, `TestDaemonReconnectsToShimIOPipesOnRestart`, `TestContainerAttach`, `TestContainerUser`, `TestContainerAttachProcess`, `TestContainerLoadUnexistingProcess`, `TestContainerUserID`, `TestContainerKillAll`, `TestDaemonRestartWithRunningShim`, `TestContainerRuntimeOptionsv2`, `TestUserNamespaces`, `TestUIDNoGID`, `TestBindLowPortNonRoot`, `TestBindLowPortNonOpt`, `TestShimOOMScore`, `TestIssue9103`, `TestIssue10589`, and `TestIssue13030`. Helpers include `numPipes`, `writeToFile`, `getLogDirPath`, `checkUserNS`, and `testUserNamespaces`.

## Control Flow And State
Most tests create a client, fetch or load `testImage`, create a container with a snapshot/spec, create a task, wait/start/kill/delete it, and assert kernel-visible state. The cgroup tests inspect cgroup v1 or v2 memory limits and shim process membership. The restart tests restart the package-level daemon and verify reconnect to running shims and log pipes. The attach tests use `directIO` and FIFO-backed stdin/stdout to prove `Task` and `Process` reload/attach behavior. The user namespace suite creates remapped snapshots or views, runs as a mapped user, and validates exit codes and setuid-bit preservation. Regression tests use `runc-fp` failpoints and FIFOs to force races around killed init processes, delayed exec startup, and parallel unpack whiteout handling.

## Persistence And Integration Points
The file touches containerd metadata, snapshotter state, shim sockets under `defaultState`, cgroup filesystems, `/proc`, OOM score files, runtime options, image rootfs metadata, and failpoint-controlled runc binaries. It also integrates with cgroups v1/v2 libraries, kernel user namespaces, overlay/native snapshot behavior, client event/status APIs, and the daemon restart helper.

## Risks And Test Signals
These tests are sensitive to root privileges, cgroup mode, available `runc-fp`, `lsof`, host user namespace support, and runtime flavor. Failures indicate high-risk regressions: resource updates not applied, leaked pipes or sockets, lost shim log forwarding after restart, broken attach semantics, incorrect UID/GID resolution, escaped child processes, OOM-score mismatch, bad runtime option propagation, exec/init race bugs, or incorrect whiteout processing during parallel unpack.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_linux_test.go -->
