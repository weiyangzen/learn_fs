# sources/distributed-fs/ceph-client/fs/resctrl/Kconfig

Purpose: Defines configuration switches for the CPU resource control filesystem and related architecture-dependent features.

Important APIs, types, and functions: Defines `RESCTRL_FS`, `RESCTRL_FS_PSEUDO_LOCK`, and `RESCTRL_RMID_DEPENDS_ON_CLOSID`. `RESCTRL_FS` depends on `ARCH_HAS_CPU_RESCTRL`, selects `KERNFS`, and selects `PROC_CPU_RESCTRL` when `PROC_FS` is enabled.

Control flow: During configuration, enabling `RESCTRL_FS` includes the mountable resctrl filesystem for hardware cache and memory-bandwidth control/monitoring. The pseudo-lock and RMID/CLOSID dependency symbols are internal bools selected or depended on by architecture code and resctrl implementation code.

State and persistence: No runtime state is stored here. The selected options decide whether resctrl code is compiled and whether optional pseudo-lock and allocator behavior is available.

Dependencies and integration points: Integrates architecture resource-control capabilities with kernfs, procfs support, and the resctrl build rules. Documentation is referenced at `Documentation/filesystems/resctrl.rst`.

Risks and test signals: Risks include enabling resctrl without architecture support, missing kernfs/proc dependencies, or inconsistent pseudo-lock configuration. Test with architectures that support and do not support CPU resctrl, with and without procfs, and with pseudo-lock capable configs.
