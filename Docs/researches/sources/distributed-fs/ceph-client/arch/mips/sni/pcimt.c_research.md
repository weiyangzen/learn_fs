# sources/distributed-fs/ceph-client/arch/mips/sni/pcimt.c

Purpose: PCIMT board setup, serial/CMOS resources, and interrupt demultiplexing.

Important APIs/types/functions: `sni_pcimt_detect`, `sni_pcimt_resource_init`, `enable_pcimt_irq`, `disable_pcimt_irq`, `pcimt_hwint0/1/3`, `sni_pcimt_hwint`, `sni_pcimt_irq_init`, `sni_pcimt_init`.

Control flow and state: detects PCIMT variant registers, initializes onboard resources, sets IRQ chips for chipset lines, demultiplexes CP0 pending bits into board IRQs and cascaded ISA, and registers serial/RTC/platform devices at device init.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: interrupt masks are board-register side effects; variant detection affects resource offsets; wrong CP0 pending priority can starve lower sources.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
