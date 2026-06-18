# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_mcpcia.h

This header describes MCPCIA/Turbolaser multi-hose core logic. It defines per-MID sparse/dense/I/O/config/CSR address spaces, interrupt registers, HAE registers, error and scatter-gather window CSRs, default hose bias values, DAC offset, and an uncorrected machine-check frame.

Important APIs are `mcpcia_ioread8/16/32/64`, `mcpcia_iowrite8/16/32/64`, `mcpcia_ioportmap`, `mcpcia_ioremap`, `mcpcia_is_ioaddr`, and `mcpcia_is_mmio`. Like CIA, byte/word accesses use sparse encodings and HAE-like state, while long/quad dense accesses are simpler. The `MCPCIA_FROB_MMIO` macro adjusts MMIO addresses depending on dense/sparse treatment.

State includes MCPCIA CSRs, interrupt masks, PCI windows, HAE registers, and machine-check data. Integration is with `asm/io.h`, PCI controller setup, DMA TBI/window code, and platform interrupt handlers. Risks are hose/MID mapping errors, sparse memory masks, one-window HAE assumptions, and multi-hose I/O address canonicalization. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
