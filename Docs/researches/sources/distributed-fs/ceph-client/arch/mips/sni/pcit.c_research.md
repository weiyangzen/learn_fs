# sources/distributed-fs/ceph-client/arch/mips/sni/pcit.c

Purpose: PCIT and PCIT-Cplus board setup, devices, and IRQ handling.

Important APIs/types/functions: 8250 resources for base/Cplus variants, CMOS resource, `sni_pcit_resource_init`, `enable_pcit_irq`, `disable_pcit_irq`, `pcit_hwint*`, `sni_pcit_irq_init`, `sni_pcit_cplus_irq_init`, `sni_pcit_init`.

Control flow and state: resource setup registers variant serial/RTC devices; IRQ setup configures chipset masks and board-specific demux routines; Cplus uses a different CP0 pending map than base PCIT.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: variant-specific IRQ maps and serial IRQs are easy to regress; fixed resources rely on board type detection; ISA cascade failure leaves legacy devices unusable.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
