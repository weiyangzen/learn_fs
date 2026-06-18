# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/irq_tx4927.c

Purpose: TX4927 interrupt-controller initialization wrapper.

Important APIs/types/functions: `tx4927_irq_init` calls the generic TXX9 IRQ init with TX4927 register base and interrupt count.

Control flow and state: early board IRQ setup installs the SoC interrupt controller before board cascades/devices are enabled.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: wrong base/count breaks all SoC interrupts.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
