# sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/irq.c

Purpose: RBTX4927 board-level IRQ routing and dispatch.

Important APIs/types/functions: board irq setup helpers, PCI/IOC interrupt mapping, `toshiba_rbtx4927_irq_setup`, dispatch callback for TXX9 core.

Control flow and state: initializes SoC IRQs, board external interrupt controller/GPIO lines, PCI IRQ mapping, and returns IRQ numbers to generic `plat_irq_dispatch` through `txx9_irq_dispatch`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: board wiring tables must match RBTX4927/RBTX4937 variants; PCI slot/pin routing errors break devices.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
