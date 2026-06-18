# sources/distributed-fs/ceph-client/include/linux/mvebu-pmsu.h

Purpose: declares the Marvell EBU PMSU dynamic frequency scaling request hook with a stub for non-MVEBU builds.

Important APIs and types: `mvebu_pmsu_dfs_request(int cpu)` is exported when `CONFIG_MACH_MVEBU_V7` is enabled and otherwise inlines to `-ENODEV`.

Control flow: CPU/clock/power-management code calls this helper to request a DFS transition for a CPU on supported MVEBU V7 platforms. Unsupported builds fail fast without requiring callers to carry their own `#ifdef`.

State and persistence: no state is stored here. Actual CPU power/frequency state is owned by PMSU/platform code and hardware.

Dependencies and integration points: integrates MVEBU platform support with generic callers that may compile on many architectures. The fallback uses the common `-ENODEV` capability-absent convention.

Risks and test signals: risks include callers treating `-ENODEV` as a transient failure, missing errno includes through transitive dependencies, and platform support drift. Test MVEBU and non-MVEBU builds, DFS request success/failure, CPU hotplug interactions, and callers' handling of unsupported platforms.
