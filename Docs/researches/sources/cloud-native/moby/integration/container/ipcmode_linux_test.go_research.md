# sources/cloud-native/moby/integration/container/ipcmode_linux_test.go

Purpose: Linux IPC namespace and `/dev/shm` behavior tests for container modes, daemon defaults, config-file defaults, and older-client compatibility.

Important APIs and flow: `testIpcCheckDevExists` scans host `/proc/self/mountinfo` for a major:minor pair. `testIpcNonePrivateShareable` starts a container with `IpcMode` and checks the container's `/dev/shm` mount pair against host mountinfo. `testIpcContainer` validates `--ipc=container:<id>` works only with shareable donors. Host mode writes to `/dev/shm` and reads from the host. Daemon default tests start child daemons with `--default-ipc-mode` or config files. `TestIpcModeOlderClient` uses API v1.39 to assert legacy shareable default.

State and dependencies: Uses running containers, host `/dev/shm`, daemon restarts, and config files. Skips remote, user namespace, and rootless cases where host IPC sharing is unavailable.

Risks and signals: It catches IPC isolation/sharing regressions, daemon default persistence bugs, and API compatibility breaks for pre-1.40 clients.
