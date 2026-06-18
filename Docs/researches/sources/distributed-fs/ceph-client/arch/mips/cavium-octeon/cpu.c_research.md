# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/cpu.c

Purpose: Cavium Octeon platform source `cpu.c`.

Important APIs and functions: key functions include cnmips_cu2_setup. It provides Octeon-specific CPU, timing, DMA, or executive services.

Control flow: selected by Octeon Kconfig/Makefile entries and invoked from MIPS architecture hooks or Octeon executive callers during boot and runtime.

State and persistence: modifies boot/runtime architecture state only: coprocessor notifier registration, timing constants, DMA translation callbacks, or bootmem-resident executive structures depending on the file.

Dependencies and integration points: includes/integrates with linux/init.h, linux/irqflags.h, linux/notifier.h, linux/prefetch.h, linux/ptrace.h, linux/sched.h, linux/sched/task_stack.h, asm/cop2.h, asm/current.h, asm/mipsregs.h; wider integration is with Octeon firmware data, CP0 registers, PCI/DMA, clocksource, SMP, and executive helper libraries.

Risks and test signals: hardware-generation assumptions are central. Test with Octeon defconfigs, SMP boot, clocksource stability, PCI/DMA I/O, and firmware bootmem behavior.
