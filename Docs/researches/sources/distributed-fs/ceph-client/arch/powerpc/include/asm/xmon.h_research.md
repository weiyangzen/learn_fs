<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xmon.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xmon.h

Purpose: Declares hooks for the PowerPC xmon kernel debugger and its printk-style output function.

Important APIs/types/functions: `xmon_setup()`, `xmon(struct pt_regs *)`, `xmon_irq()`, SMP `cpus_are_in_xmon()`, and always-declared `xmon_printf()`.

Control flow: When `CONFIG_XMON` is enabled, exception/IRQ paths can enter xmon and setup registers debugger hooks; otherwise setup is a no-op while `xmon_printf` remains available to linked code.

State and persistence: Debugger state is implemented elsewhere; this header only exposes entry points.

Dependencies and integration points: Depends on irq return types and `pt_regs`. Integrated with trap, IRQ, SMP, and debug code.

Risks: Entry points run in fragile exception contexts. Incorrect stubbing can break builds with xmon disabled.

Test signals: CONFIG_XMON on/off builds, debugger entry via keyboard/sysrq/NMI paths, SMP rendezvous tests, and xmon output smoke tests.

Source read size: 29 lines, 611 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xmon.h -->
