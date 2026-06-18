<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_cgroup_writable_linux_test.go -->
# sources/cloud-native/containerd/integration/container_cgroup_writable_linux_test.go

## Purpose
Tests the CRI runtime `cgroup_writable` setting on cgroup v2 by verifying whether a container can create a directory under `/sys/fs/cgroup`.

## APIs, Types, And Functions
The file defines `newContainerdProcess` and `TestContainerCgroupWritable`. It uses temporary containerd config files, `newCtrdProc`, `remote.NewRuntimeService`, CRI image pull helpers, `RunPodSandbox`, `CreateContainer`, `StartContainer`, `ContainerStatus`, and `ExecSync`.

## Control Flow And State
Each table case starts a separate containerd process with `cgroup_writable = true` or `false`, opens a CRI runtime service, pulls BusyBox, creates and starts a sandbox/container, confirms it is running, then executes `mkdir sys/fs/cgroup/dummy-group`. The writable case expects success and empty stderr; the readonly case expects an error containing a read-only filesystem message.

## Persistence And Integration Points
State includes temporary daemon config/root, CRI pods/containers, image content, and cgroup filesystem permissions visible inside the container. Cleanup removes pods, closes the runtime service, and terminates the daemon.

## Risks And Test Signals
The test requires cgroup v2 and root-capable CRI integration. Failures indicate the runtime config is ignored, mount permissions are wrong, or cgroup filesystem error reporting changed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_cgroup_writable_linux_test.go -->
