<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_test.go -->
# sources/cloud-native/containerd/integration/client/container_test.go

## Purpose
This is the broad cross-platform client integration suite for container, task, process, IO, metadata, event, and daemon restart behavior. It functions as an executable contract for the public containerd client API around `Container`, `Task`, `Process`, images, snapshots, specs, labels, extensions, runtime path selection, waits, deletes, and kill semantics.

## APIs, Types, And Functions
Key tests cover list/create/start/output/wait/exec/large exec args/PIDs/close IO/delete running/kill/missing binaries/stopped wait/force delete/hostname/metrics/extensions/update/info/labels/hooks/shim socket length/large TTY output/short task PID/events/daemon restart/task spec/container image/no image/no stdin/username/PTY. Helpers include `empty`, `readShimPath`, `copyShim`, `withStdout`, `withProcessTTY`, `initContainerAndCheckChildrenDieOnKill`, and the `directIO` wrapper implementing `IOCreate`, `IOAttach`, `Cancel`, `Close`, and `Delete`.

## Control Flow And State
The common pattern is to create a namespaced client, load or pull an image, create a container with `WithNewSnapshot` and `WithNewSpec`, create a task with a selected IO creator, wait before start, start, assert status/output/events, then delete task/container with snapshot cleanup. Metadata tests mutate and reload container labels, extensions, specs, images, and info. Regression tests subscribe to task exit events to ensure no duplicate exit event after delete and no exit event for a command-not-found task. Restart coverage restarts the global daemon while a task is running, expects the first wait to fail due to transport closure, waits for daemon serving, then waits/kills the same task again.

## Persistence And Integration Points
State is persisted through containerd metadata, content/images, snapshots, runtime shim directories, FIFO directories, event streams, task status, and OCI specs marshaled through typeurl. The file integrates with runc for one test that force-deletes a container behind containerd, the `containerd oci-hook` command, platform-specific helper functions, and runtime v2 shim path files.

## Risks And Test Signals
The suite catches API contract regressions that unit tests miss: incorrect exit-code propagation, missing pid accounting, leaked or blocked IO, wrong error classes, unsafe deletion while running, broken metadata update/load, task metrics availability, event duplication, shim path length limits, PTY corruption, and restart reconnection failures. Some tests are platform-specific or flaky-sensitive because they rely on process timing, Windows behavior, terminal output, and host tools such as `ps`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_test.go -->
