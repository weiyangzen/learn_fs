# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.h

Purpose: user-space compatibility layer for sched_ext loader programs, primarily using vmlinux BTF to adapt skeleton struct_ops fields and enum values to the running kernel.

Important APIs/macros: `__COMPAT_load_vmlinux_btf()`, `__COMPAT_read_enum()`, `__COMPAT_has_ksym()`, and `__COMPAT_struct_has_field()` query kernel BTF. `SCX_OPS_FLAG()` and `SCX_PICK_IDLE_FLAG()` expose enum-derived flags. `scx_hotplug_seq()` reads `/sys/kernel/sched_ext/hotplug_seq`. `SCX_OPS_OPEN()`, `SCX_OPS_LOAD()`, and `SCX_OPS_ATTACH()` wrap skeleton open, enum initialization, optional op nulling for unsupported fields, UEI sizing, load, and struct_ops attach.

Control flow: loaders call `SCX_OPS_OPEN()` before setting rodata/options. The macro verifies the minimum `sched_ext_ops.dump` field, opens the skeleton, initializes hotplug sequence and generated enums, then conditionally disables callbacks not supported by the running kernel. Load and attach macros complete the lifecycle.

State and persistence: caches `__COMPAT_vmlinux_btf` in a weak global. Reads but does not persist hotplug sequence state.

Dependencies and integration: requires libbpf BTF APIs, `fcntl`, `unistd`, generated enum helpers, and `user_exit_info.h`. It is used by all sched_ext C loaders in this subset through `common.h`.

Risks: BTF must be available and accurate. `SCX_BUG_ON()` terminates on missing required BTF operations. Compatibility nulling can silently disable callbacks with only a warning, so behavior may differ on older kernels.

Test signals: run loaders against kernels with and without newer `sched_ext_ops` fields such as `cgroup_set_bandwidth`, `cgroup_set_idle`, and sub-scheduler fields; validate warnings and successful attach.
