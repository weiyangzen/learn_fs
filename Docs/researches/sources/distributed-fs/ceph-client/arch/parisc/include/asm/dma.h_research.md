# sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma.h

Purpose: defines legacy PA-RISC DMA constants and helpers for ISA/EISA-style DMA and fallback device code.

Important APIs/types/functions: provides DMA channel limits, address constraints, request/free DMA declarations, `MAX_DMA_ADDRESS`, and compatibility helpers for drivers still using legacy DMA APIs.

Control flow: old drivers reserve a channel, program a transfer through architecture support, and release the channel. Modern PCI devices usually use the generic DMA mapping API instead.

State and persistence: channel ownership and controller programming persist in platform DMA hardware. Dependencies and integration: integrates with EISA/ISA compatibility, floppy support, and machine-specific DMA setup.

Risks and test signals: incorrect address limits or channel programming can corrupt low memory. Test with floppy/legacy-device builds, DMA API debug, and platform probes that still expose ISA-compatible DMA.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
