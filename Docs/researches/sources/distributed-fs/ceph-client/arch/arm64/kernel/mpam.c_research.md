# sources/distributed-fs/ceph-client/arch/arm64/kernel/mpam.c

Purpose: Initializes arm64 MPAM requestor support and restores MPAM system registers after CPU power management events.

Important APIs and state: defines static key `mpam_enabled`, per-CPU `arm64_mpam_default` and `arm64_mpam_current`, and global `arm64_mpam_global_default`. The PM notifier `mpam_pm_notifier()` restores `MPAM1_EL1`, optional `MPAMSM_EL1`, and `MPAM0_EL1` on `CPU_PM_EXIT`. `arm64_mpam_register_cpus()` registers the CPU PM notifier and calls `mpam_register_requestor()`.

Control flow: at arch init, the code reads sanitized `MPAMIDR_EL1`, extracts maximum PARTID and PMG, and exits if MPAM is unsupported. On CPU PM exit, it writes the current per-CPU MPAM value back to relevant registers with enable bits and synchronization.

Dependencies and integration: depends on arm64 MPAM cpufeature detection, Linux MPAM core, CPU PM notifiers, jump labels/static keys, and SME support for streaming-mode MPAM register restoration.

Risks and test signals: risks are stale partition/PMG values after suspend, incorrect PARTID/PMG limits, missing SME register restore, and init ordering relative to MPAM MSC driver. Test with MPAM-enabled hardware or emulation, CPU suspend/resume, hotplug, resource control assignments, and SME-capable systems.
