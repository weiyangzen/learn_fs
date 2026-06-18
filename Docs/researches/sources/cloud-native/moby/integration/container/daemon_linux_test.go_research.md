# sources/cloud-native/moby/integration/container/daemon_linux_test.go

Purpose: Linux daemon restart recovery tests for container startability, IPC-mode persistence, host-gateway resolution, restarting-state repair, and hard-reboot-like stale running state.

Important APIs and flow: The tests use `daemon.New`, `StartWithBusybox`, `Kill`, `Restart`, `TamperWithContainerConfig`, `ContainerInspect`, `ContainerStart`, and `ContainerWait`. `getContainerdShimPid` reads `/proc/<pid>/stat` to kill the shim. Other tests inspect `/etc/hosts`, compare `HostConfig.IpcMode`, and mutate daemon container state using `realcontainer.Container` methods.

State and dependencies: These tests create isolated dockerd instances, kill daemon/shim/container processes, alter on-disk container state, and restart daemons with different flags such as `--default-ipc-mode` and `--host-gateway-ip`. They skip remote, Windows, and sometimes rootless modes.

Risks and signals: They guard restore paths after unclean shutdowns, restart policy reconciliation, health/state persistence, and default-setting changes after restart. Failures usually imply daemon startup cannot reconcile stale runtime metadata or cannot preserve already-created container configuration.
