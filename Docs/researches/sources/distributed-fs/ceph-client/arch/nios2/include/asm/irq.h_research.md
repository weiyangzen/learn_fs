# sources/distributed-fs/ceph-client/arch/nios2/include/asm/irq.h

Purpose: Nios II IRQ constants/header glue.

Important APIs/types/functions: architecture IRQ definitions such as `NR_IRQS` or include contracts for irqdomain-based sparse IRQ.

Control flow and state: provides minimal arch IRQ interface to generic interrupt code.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: must match platform interrupt controller configuration.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
