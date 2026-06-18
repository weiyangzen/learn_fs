# sources/distributed-fs/ceph-client/arch/x86/kernel/itmt.c

Purpose: Provides x86 scheduler integration for Intel Turbo Boost Max Technology 3.0. On systems where some cores have higher maximum turbo capability, this file lets platform code publish per-CPU priorities and exposes a debugfs switch so scheduler domains can prefer stronger cores.

Important APIs/types/functions: exports `sched_set_itmt_support()`, `sched_clear_itmt_support()`, `sched_set_itmt_core_prio()`, and `arch_asym_cpu_priority()`. Global state is `DEFINE_PER_CPU_READ_MOSTLY(int, sched_core_priority)`, `sched_itmt_capable`, and `sysctl_sched_itmt_enabled`. Debugfs entries are `sched_itmt_enabled` and `sched_core_priority`.

Control flow: platform or pstate code first calls `sched_set_itmt_core_prio()` per CPU, then `sched_set_itmt_support()`. Support creation registers debugfs files under `arch_debugfs_dir`, marks the machine capable, enables the scheduler feature, sets `x86_topology_update`, and calls `rebuild_sched_domains()`. Writes to debugfs go through `sched_itmt_enabled_write()`, which compares the old boolean with the new value and rebuilds sched domains only on actual change. Clearing support removes debugfs files and disables scheduler preference if it was enabled.

State and persistence: all state is in kernel memory and per-CPU variables. CPU priorities persist for the running boot only. The debugfs control is not persistent across reboot and has no on-disk backing.

Dependencies and integration points: depends on scheduler asymmetry hooks, x86 topology rebuilds, cpuset/sched-domain rebuild machinery, debugfs, and `arch_debugfs_dir` from `kdebugfs.c`. Power-management code is expected to discover ITMT capability and call these APIs.

Risks: calling support before priorities are initialized can produce misleading scheduler preference. Rebuilds must not run under CPU hotplug locks as documented. Failure after creating the first debugfs file leaves capability disabled but does not remove the first file in this implementation path, so init-error cleanup assumptions should be checked if changed.

Test signals: boot on ITMT-capable hardware should create both debugfs files, show nonzero per-CPU priorities, and rebuild sched domains when toggled. Non-capable systems should not expose the files. CPU hotplug and pstate enable/disable paths should not deadlock with topology rebuilds.
