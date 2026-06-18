# File Research: sources/block-storage/util-linux/sys-utils/chcpu.c

## Scope

Implements `chcpu`, a sysfs-based CPU hotplug/configuration utility for enabling, disabling, configuring, deconfiguring, rescanning CPUs, and setting CPU dispatch mode.

## Public And Internal APIs Covered

- Main command-line entry point.
- CPU operations: `cpu_enable()`, `cpu_configure()`, `cpu_rescan()`, `cpu_set_dispatch()`.
- CPU set parsing and discovery: `cpu_parse()`, `read_cpulist()`.

## Control Flow And Behavior

- Parses one exclusive operation: enable, disable, configure, deconfigure, dispatch, or rescan.
- Supports `--sysroot` by prefixing the sysfs path context rooted at `/sys/devices/system/cpu`.
- `read_cpulist()` determines `maxcpus` from `kernel_max` or fallback CPU count, allocates a CPU set, and reads the `online` cpulist when available.
- `cpu_enable()` writes `cpuN/online`, checks hotplug capability, avoids disabling the last online CPU, and reports already-enabled/disabled states.
- `cpu_configure()` writes `cpuN/configure`, skips non-configurable CPUs, and refuses deconfiguration while a CPU is online.
- `cpu_rescan()` writes `1` to `rescan`.
- `cpu_set_dispatch()` writes `0` or `1` to `dispatching` for horizontal or vertical dispatch mode.

## Dependencies

- util-linux `path_cxt` sysfs helpers.
- CPU set parsing from `cpuset.h`.
- Option exclusion utilities and i18n/closestream helpers.

## Risks And Invariants

- Only one primary operation may be requested.
- Partial success returns `64` (`CHCPU_EXIT_SOMEOK`) rather than generic failure.
- Disabling CPUs updates the cached online CPU set to preserve the last-online-CPU invariant.
- Sysfs attribute availability determines support for hotplug, configure, dispatching, and rescan operations.
