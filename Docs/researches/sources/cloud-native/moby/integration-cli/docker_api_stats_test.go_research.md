# sources/cloud-native/moby/integration-cli/docker_api_stats_test.go

Purpose: validates `/containers/{id}/stats` behavior for non-streaming CPU stats, stopped-container stream cleanup, network packet counters, and `one-shot` stats for containers sharing another container's network namespace.

Important APIs, types, and functions: `TestAPIStatsNoStreamGetCpu`, `TestAPIStatsStoppedContainerInGoroutines`, `TestAPIStatsNetworkStats`, `getNetworkStats`, and `TestAPIStatsNoStreamConnectedContainers`. It decodes `container.StatsResponse`, `container.NetworkStats`, and `system.Info`, and uses `request.Get`, `cli.DockerCmd`, `runSleepingContainer`, `findContainerIP`, and host `ping`.

Control flow: CPU tests run a busy shell loop, call `stats?stream=false`, and calculate CPU percentage from Linux-style `CPUStats`/`PreCPUStats` or Windows 100ns interval data. Goroutine cleanup records `/info` `NGoroutines`, opens a stats stream for a stopped container, closes it, and polls until goroutine count returns to baseline. Network stats compare packet counters before and after a host ping. Connected-container stats create a second container using `--net container:<id>` and assert `one-shot` returns exactly one JSON object.

State and persistence behavior: state is transient daemon/container resource accounting. Tests depend on counters, daemon goroutine counts, and network namespace sharing. There is no file persistence. HTTP bodies are explicitly closed to trigger stream teardown.

Dependencies and integration points: integrates Engine stats API, daemon info API, BusyBox workloads, host `ping`, platform-specific counter math, cgroup version gating, local-daemon requirements, and Windows containerd skips. It relies on external process execution for `ping` and includes a Linux AppArmor workaround using the dynamic linker path.

Risks and edge cases: CPU percentage can be zero on unsupported/idle accounting paths, so cgroup v2 is skipped. Goroutine-count assertions can be noisy if unrelated daemon work occurs. Network packet assertions account for ARP on Linux but still depend on host reachability and ping availability. The connected-container test uses a 10-second context to prevent hangs, signaling prior risk in shared-network stats collection.

Test signals: covers JSON content type, non-zero CPU accounting, stream goroutine cleanup after client disconnect, RX/TX packet counter increases after traffic, and one-shot stats returning a single object with the requested container ID for container network namespace sharing.
