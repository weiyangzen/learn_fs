# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/smp.c

Purpose: Provides pSeries SMP operations for CPU startup, per-CPU interrupt setup, VPA setup, IPI routing, and NMI IPI support.

Important APIs/types/functions: Defines `of_spin_mask`, `smp_query_cpu_stopped()`, `smp_startup_cpu()`, `smp_setup_cpu()`, `smp_pSeries_kick_cpu()`, `pseries_smp_prepare_cpu()`, `dbell_or_ic_cause_ipi()`, `pseries_cause_nmi_ipi()`, `pSeries_smp_probe()`, `pseries_smp_ops`, and `smp_init_pseries()`.

Control flow: Early init installs pSeries SMP ops and marks CPUs already spinning in OF hold loops when stopped-state query is unavailable. CPU kick starts a CPU through RTAS `start-cpu` unless it is already spinning, then sets PACA `cpu_start`. Probe initializes XIVE or XICS SMP support and may replace controller IPIs with doorbell-or-controller IPIs when hardware, SMT, hypervisor, and secure-guest conditions make that useful.

State and persistence: Tracks OF-spinning CPUs in `of_spin_mask` and stores the original interrupt-controller IPI function in `ic_cause_ipi`. Per-CPU setup initializes XIVE/XICS and VPA state.

Dependencies and integration points: Depends on RTAS CPU calls, PACA startup flags, XICS/XIVE, doorbells, VPA, KVM guest detection, secure guest checks, and generic powerpc SMP ops.

Risks: CPU startup differs for OF-started, stopped, kexec, and missing-token cases. Doorbell optimization must avoid slow or unsupported KVM emulation and secure-guest instruction visibility problems. NMI IPI uses hypervisor system-reset signaling and must tolerate failure.

Test signals: Secondary CPU boot, CPU hotplug, kexec CPU states, XIVE and XICS systems, SMT doorbell IPI delivery, KVM and secure guest behavior, RTAS query/start failures, and NMI IPI all-others paths.

Source read size: 282 lines, 7137 bytes.
