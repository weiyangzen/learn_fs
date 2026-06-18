# sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux.go

Purpose: Linux cgroup v1 and generic kernel feature detection.

APIs and flow: `New` dispatches to v2 or `newV1`. v1 mount discovery caches cgroup mountinfo once, parses `/proc/self/cgroup`, maps subsystem mountpoints, then applies collectors for memory, CPU, blkio, cpuset, pids, devices, networking, AppArmor, seccomp, cgroup namespaces, and time namespaces. `parseUintList` and `isCpusetListAvailable` validate cpuset requests with a maximum bound.

State and dependencies: reads procfs, sysfs, cgroup files, and mountinfo; mountinfo is cached in package globals.

Integration points: used by Docker daemon validation/reporting paths. Depends on containerd seccomp/cgroups and Moby mountinfo.

Risks and tests: cached mountinfo assumes mounts do not change. Both v1 cpuset collection and v2 counterpart parse `info.Cpus` when building `MemSets`, which looks like a bug. Tests cover parse bounds, proc bools, cgroup file detection, and generic feature flags.
