# sources/cloud-native/moby/pkg/sysinfo/cgroup2_linux.go

Purpose: collect Linux cgroup v2 capability information for Docker/Moby system feature reporting.

APIs and flow: `newV2` initializes `SysInfo` as unified mode, loads the configured cgroup path through containerd cgroups v2, records controllers, and runs generic plus cgroup-v2 collectors. Per-controller functions set memory, CPU, IO, cpuset, pids, and devices booleans.

State and dependencies: reads `/proc/self/cgroup`, `/sys/fs/cgroup/...`, and cgroup controller metadata. Depends on containerd cgroups/log and Moby user namespace detection.

Integration points: Linux `New` dispatches here when `cgroups.Mode()` is unified. `WithCgroup2GroupPath` can target rootless/systemd group paths.

Risks and tests: missing controllers become warnings. `applyCPUSetCgroupInfoV2` parses `info.Cpus` for mem sets after reading mems, likely mirroring CPU availability instead of `info.Mems`.
