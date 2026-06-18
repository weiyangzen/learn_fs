# sources/distributed-fs/ceph-client/arch/s390/kernel/nmi.c

Purpose: machine-check/NMI handling for s390, including MCESA allocation, emergency reporting, recoverability decisions, guest machine-check backup, deferred handling, and control-register mask setup.

Important APIs and state: per-CPU `cpu_mcck` accumulates `kill_task`, `channel_report`, `warning`, `stp_queue`, and machine-check code. Public helpers include `nmi_alloc_mcesa_early()`, `nmi_alloc_mcesa()`, `nmi_free_mcesa()`, `s390_handle_mcck()`, and `s390_do_machine_check()`.

Control flow: early and hotplug allocation provide machine-check extended save areas for vector/guarded-storage capable systems. Fatal damage path emergency-stops CPUs, resets via DIAG 308, disables low-address protection, prints lowcore/register state through SCLP emergency output, restores analyzable state, and enters disabled wait. The NMI handler enters irqentry NMI context, validates register-save bits, distinguishes host vs KVM guest damage, backs up guest interruption data when needed, handles storage/timing/channel/warning/STP subclasses, schedules deferred machine-check work, and clears guest flags.

Dependencies and integration: uses lowcore, control registers, SCLP, SMP emergency stop, KVM SIE state, STP, CRW handling, process signal delivery, vtime, irq stats, vector/GS save helpers, and kprobes blacklist markers.

Risks and test signals: recovery logic is safety-critical; wrong validity decisions can kill tasks, damage guests, or hang systems. Test with machine-check injection/facility simulation, KVM guest paths, warning masks, STP external damage, vector/GS systems, crash dump readability, and repeated instruction-processing damage thresholds.
