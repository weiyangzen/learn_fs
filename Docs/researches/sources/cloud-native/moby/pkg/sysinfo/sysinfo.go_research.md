# sources/cloud-native/moby/pkg/sysinfo/sysinfo.go

Purpose: define the public `SysInfo` model for kernel/container runtime capability reporting.

APIs and types: `Opt` customizes `New`. `SysInfo` embeds memory, CPU, blkio, cpuset, and pids cgroup capability structs plus AppArmor, Seccomp, namespace, networking, device, unified mode, warnings, and internal cgroup mount/controller state. Cpuset helpers expose availability checks.

State and persistence: struct instances are snapshots of host state; internal maps hold parsed cgroup paths/controllers.

Dependencies and integration: platform-specific files populate this model. Consumers can inspect booleans and warnings but should not parse warning text.

Risks and tests: cpuset availability depends on parsed maps being populated; non-Linux returns mostly empty state.
