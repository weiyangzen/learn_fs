# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/smp.c

Purpose: SMP operations for CHRP systems using OpenPIC/MPIC and RTAS timebase transfer.

Important APIs and control flow: `smp_chrp_kick_cpu` writes the target CPU number to `KERNELBASE`, flushes that cache line, and returns success so secondary firmware/hold code can observe it. `smp_chrp_setup_cpu` calls `mpic_setup_this_cpu`. `chrp_smp_ops` delegates probing and IPIs to MPIC helpers and timebase handoff to `rtas_give_timebase`/`rtas_take_timebase`.

State, dependencies, and risks: state is the externally installed `smp_ops` table and the magic word at `KERNELBASE`. Dependencies include MPIC initialization, RTAS timebase services, and secondary CPU boot conventions. Risks are platform-specific secondary release semantics and invalid use on Pegasos systems without MPIC, which `setup.c` avoids. Test signals are secondary CPU bring-up, IPI delivery, synchronized timebase, and no crash when SMP is disabled or MPIC is absent.
