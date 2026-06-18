<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/types.h

Purpose: provides architecture type selections and includes generic Linux type definitions for LoongArch.
Important APIs and types: defines LoongArch-specific DMA/physical address typedef availability through generic headers and architecture config.
Control flow: no runtime flow; compile-time type contract only.
State and persistence: type widths shape ABI and in-memory structures.
Dependencies and integration: consumed by kernel and UAPI headers that require exact integer and address widths.
Risks and test signals: type-width mistakes cause ABI or DMA address truncation. Signals are allmodconfig builds and sparse/compile checks across 32-bit and 64-bit variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/types.h -->
