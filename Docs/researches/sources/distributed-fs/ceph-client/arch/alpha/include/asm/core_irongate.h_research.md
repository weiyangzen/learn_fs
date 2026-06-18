# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_irongate.h

This header models the AMD-751 Irongate chipset used on Nautilus EV6 systems. It defines PCI configuration register structures `Irongate0` and `Irongate1`, CSR/config address macros, memory/I/O/config/IACK spaces, the `IronECC` CSR pointer, and an Irongate machine-check frame.

Runtime APIs are simple linear mapping helpers: `irongate_ioportmap`, external `irongate_ioremap`/`irongate_iounmap`, `irongate_is_ioaddr`, and `irongate_is_mmio`. It then sets `__IO_PREFIX=irongate` and marks byte/word and long/quad I/O and MMIO operations as trivial so `io_trivial.h` supplies direct loads/stores.

State is chipset PCI/AGP/GART/ECC CSRs and mapped I/O addresses. Integration is with `asm/io.h`, PCI/AGP setup, DMA/IOMMU paths, and machine-check reporting. Risks include the 44-bit physical address split, GART/AGP register layout drift, and distinguishing MMIO from port space using address bits. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
