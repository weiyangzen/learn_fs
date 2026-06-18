# sources/distributed-fs/ceph-client/arch/arm/mach-actions/platsmp.c

Purpose: implements SMP bring-up for Actions S500 systems. Key routines are `s500_smp_prepare_cpus`, `s500_smp_boot_secondary`, `s500_wakeup_secondary`, and the `CPU_METHOD_OF_DECLARE` binding for `actions,s500-smp`.

Control flow maps timer and SPS registers from DT, optionally maps/enables Cortex-A9 SCU, powers CPU2/CPU3 through `owl_sps_set_pg`, writes `secondary_startup` physical addresses and boot flags into timer scratch registers, sends `sev`, pokes reschedule IPI, then clears scratch values. Persistent state is mapped base pointers and SCU core count. Dependencies include DT compatible nodes, SPS helper, SCU support, `secondary_startup`, barriers, and IPI tracing. Risks are missing DT nodes, invalid CPU ids above 3, power-domain ack failures, and scratch-register protocol mismatches. Test signals include secondary CPU online logs, SCU enablement, and failure logs for missing timer/SPS/SCU nodes.
