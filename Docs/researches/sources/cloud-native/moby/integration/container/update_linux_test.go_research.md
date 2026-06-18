# sources/cloud-native/moby/integration/container/update_linux_test.go

Purpose: Linux-specific integration coverage for `ContainerUpdate`, verifying that resource changes are persisted in inspect data and, where possible, actually applied to cgroup files inside a running container.

Important APIs and helpers: `TestUpdateMemory`, `TestUpdateCPUQuota`, `TestUpdatePidsLimit`, `TestUpdateBlkioThrottleDevices`, `blkioTestDevice`, and `parseIOMax`. The tests use `client.ContainerUpdateOptions`, `container.Run`, `container.Exec`, daemon capability flags from `testEnv.DaemonInfo`, and direct cgroup file reads.

Control flow: each test starts a busybox container, calls `ContainerUpdate`, inspects the container to verify `HostConfig.Resources`, then reads relevant cgroup files. Memory checks branch between cgroup v1 memory and memsw files and cgroup v2 `memory.max`/`memory.swap.max`. CPU quota handles the cgroup v2 runc workaround by setting `CPUPeriod`. PIDs cases table-drive old API behavior, unset values, and cgroup `max` output. Blkio finds the root block device through `/sys/dev/block`, updates all four throttle lists, and on cgroup v2 parses `io.max`.

State and persistence: the file validates both daemon metadata persistence through `ContainerInspect` and runtime kernel state through cgroup files. Old API behavior for PIDs intentionally preserves the previous value. Blkio persistence is asserted even on cgroup v1 where in-container throttle files are not mounted.

Dependencies and integration: depends on Linux cgroups, `x/sys/unix`, `/sys`, daemon feature flags, the integration container helpers, and the Moby API client. It integrates API-level update semantics with OCI runtime/cgroup application.

Risks: tests are environment-sensitive: cgroup driver `none`, missing memory/swap/PIDs support, root filesystem on unusual devices, or cgroup namespace visibility can skip or destabilize assertions. The blkio helper assumes the filesystem backing `/` maps to a usable `/dev/<name>` path.

Test signals: strong signal that live resource updates work across cgroup v1/v2 for memory, swap, CPU quota, PIDs, and blkio throttling, including compatibility for API 1.24.
