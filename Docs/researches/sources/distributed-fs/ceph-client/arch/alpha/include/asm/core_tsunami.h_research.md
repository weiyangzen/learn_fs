# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_tsunami.h

This header defines Tsunami/Typhoon EV6 core logic. It models CChip, DChip, and PChip CSRs; PChip error, window base, control, and error-mask unions; hose address spaces; I/O and memory bias; DAC offset; and an empty Tsunami machine-check system-data structure placeholder.

Important APIs are external `tsunami_ioportmap` and `tsunami_ioremap`, inline `tsunami_is_ioaddr` and `tsunami_is_mmio`, and `io_trivial.h`-supplied direct I/O/MMIO access under `__IO_PREFIX=tsunami`. `TSUNAMI_bootcpu` tracks platform boot CPU identity externally.

State includes CChip/PChip registers, PCI windows/TLB invalidation registers, and mapped I/O. Integration is through Alpha I/O, PCI hose setup, DMA/IOMMU windows, and error handlers. Risks include hose address shifts, 40-bit DAC offset, PChip bitfield correctness, and assuming iounmap is trivial. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
