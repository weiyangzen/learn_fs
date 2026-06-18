# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/smp.c

Purpose: SMP bring-up support for Microwatt FPGA systems.

Important APIs and control flow: `microwatt_init_smp` early-maps a hard-coded syscon block, reads CPU count from `SYSCON_CPU_CTRL`, installs `microwatt_smp_ops` when more than one CPU exists, writes secondary boot instructions at `KERNELBASE`, enables all CPUs through syscon, waits briefly for `__secondary_hold_acknowledge`, and unmaps. SMP ops use XICS probe/setup and generic CPU kick with muxed IPI handling.

State, dependencies, and risks: state is global `smp_ops`, code patched at physical/virtual `KERNELBASE`, and syscon CPU control bits. Dependencies include early_ioremap, raw PowerPC opcodes, XICS SMP helpers, secondary hold protocol, and a hard-coded syscon address noted as needing DT data. Risks are address mismatch on future Microwatt variants, timeout without error propagation, cache coherency of patched boot code, and booting more CPUs than assumed by bitmask width. Test signals are secondary CPU online, XICS per-CPU setup, time to acknowledge hold, and no regression on single-CPU systems.
