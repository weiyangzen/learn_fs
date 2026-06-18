<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon_config_linux_test.go -->
# sources/cloud-native/containerd/integration/client/daemon_config_linux_test.go

## Purpose
Verifies Linux daemon configuration paths that are hard to exercise through the default daemon: runtime root override and custom cgroup path creation.

## APIs, Types, And Functions
`TestDaemonRuntimeRoot` uses `newDaemonWithConfig`, `WithRuntime`, runc `options.Options{Root: ...}`, `WithNewSnapshot`, and task lifecycle APIs. `getCgroupPath` parses `/proc/self/mountinfo`. `TestDaemonCustomCgroup` checks `[cgroup].path` for cgroup v1.

## Control Flow And State
The runtime-root test starts a temporary daemon, pulls an image, creates a task with a custom runc root, asserts that `runtimeRoot/<namespace>/<id>` exists, then kills the task. The custom-cgroup test skips on unified cgroup v2, discovers mounted v1 controller paths, starts a daemon with a generated cgroup path, and asserts that known controllers create that path, cleaning it afterward.

## Persistence And Integration Points
The tests persist temporary daemon roots/states, custom runc runtime directories, and cgroup directories under host controller mounts. They integrate with daemon config loading, runc runtime options, the global test namespace, and Linux cgroup filesystems.

## Risks And Test Signals
Failures signal ignored runtime root configuration, ignored daemon cgroup path configuration, cgroup mount parsing drift, or cleanup problems that can leave host cgroup directories behind. The custom cgroup test is intentionally cgroup-v1-only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon_config_linux_test.go -->
