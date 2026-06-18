# sources/distributed-fs/ceph-client/arch/nios2/include/asm/irqflags.h

Purpose: Nios II local IRQ flag primitives.

Important APIs/types/functions: `arch_local_save_flags`, `arch_local_irq_restore`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_irqs_disabled_flags`, `arch_local_irq_save`.

Control flow and state: uses Nios II control-register reads/writes for status/PIE bits to save, restore, disable, and enable local interrupts.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: control-register hazards and exact status-bit masks are critical; bugs manifest as lost interrupts or unsafe critical sections.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
