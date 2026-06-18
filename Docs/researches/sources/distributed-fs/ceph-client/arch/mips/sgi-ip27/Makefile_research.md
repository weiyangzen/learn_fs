# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Makefile

Purpose: build composition for SGI IP27 support. It links bus-error, IRQ, init, KL config, NUMA, memory, NMI, reset, timer, and Crosstalk code, with optional early console and SMP support.

Important APIs and control flow: `obj-y` lists the mandatory IP27 objects. `ip27-console.o` is selected by `CONFIG_EARLY_PRINTK`; `ip27-smp.o` is selected by `CONFIG_SMP`.

State, persistence, and integration: no runtime state is created, but object selection controls whether `ip27_smp_ops` and early `prom_putchar()` are available. Dependencies include IP27 architecture config and SMP/early-printk choices. Risks include missing SMP hooks in a multi-CPU kernel or no early console for firmware debugging. Test signals are successful link and expected symbols in the built image.
