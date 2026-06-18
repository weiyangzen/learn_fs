# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcic.h

Purpose: JavaEngine 1 PCIC controller contract: MMIO register offsets, interrupt/status bits, the `linux_pcic` controller structure, and optional probe/IRQ/time hooks under `CONFIG_PCIC_PCI`.

Important APIs/types/functions: types `linux_pcic`; functions/helpers `pcic_present`, `pcic_probe`, `pci_time_init`, `sun4m_pci_init_IRQ`; macros/constants `__SPARC_PCIC_H`, `PCI_SPACE_SIZE`, `PCI_DIAGNOSTIC_0`, `PCI_SIZE_0`, `PCI_SIZE_1`, `PCI_SIZE_2`, `PCI_SIZE_3`, `PCI_SIZE_4`, `PCI_SIZE_5`, `PCI_PIO_CONTROL`, `PCI_DVMA_CONTROL`, `PCI_DVMA_CONTROL_INACTIVITY_REQ`, `PCI_DVMA_CONTROL_IOTLB_ENABLE`, `PCI_DVMA_CONTROL_IOTLB_DISABLE`, `PCI_DVMA_CONTROL_INACTIVITY_ACK`, `PCI_INTERRUPT_CONTROL`, `PCI_CPU_INTERRUPT_PENDING`, `PCI_DIAGNOSTIC_1`, plus 62 more.

Control flow: The file is driven by preprocessor gates such as `__SPARC_PCIC_H`, `__ASSEMBLER__`, `CONFIG_PCIC_PCI`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP, timekeeping, PCI paths rather than through standalone functions.

State and persistence behavior: State lives in mapped PCIC registers, `struct resource` ranges, the embedded `linux_pbm_info`, and interrupt mapping arrays; disabled builds provide zero/no-op stubs.

Dependencies and integration points: Includes/dependencies: `linux/types.h`, `linux/smp.h`, `linux/pci.h`, `linux/ioport.h`, `asm/pbm.h`. Integration points include memory-management, TLB/MMU, SMP, timekeeping, PCI; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Exercise PCIC probe on JavaEngine/sun4m PCI, register resource reservation, IOTLB enable/disable, interrupt pending/clear paths, and timer IRQ setup.
