# sources/distributed-fs/ceph-client/arch/nios2/kernel/irq.c

Purpose: initializes the Nios II IRQ domain and irq_chip, maintains the ienable mask, and dispatches hardware
interrupt vectors from assembly entry.

Important APIs/types/functions: functions: `do_IRQ`, `chip_unmask`, `chip_mask`, `irq_map`, `init_IRQ`; prototypes: `irq_enter`,
`BUG_ON`; types: `pt_regs`, `irq_domain`, `device_node`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/interrupt.h`, `linux/irqdomain.h`, `linux/of.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
