# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-common.h

Purpose: shared IP27 declarations for cross-file platform hooks.

Important APIs and control flow: it declares `master_nasid`, CPU/node probing, HUB RTC clockevent/source setup, NMI installation, IPI setup, bus-error init, reboot setup, SMP ops, first-free-node memory calculation, per-CPU init, and kernel text replication helpers.

State, persistence, and integration: it centralizes the IP27 internal interface between init, memory, SMP, IRQ, timer, NMI, and reset objects. Dependencies include SGI SN NASID types and `plat_smp_ops`. Risks are tight coupling through global functions and no type-level ownership boundaries for hardware state. Test signals are compile-time consistency and successful linking of IP27 objects under SMP and non-SMP configs.
