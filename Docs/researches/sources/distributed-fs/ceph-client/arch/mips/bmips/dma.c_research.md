# sources/distributed-fs/ceph-client/arch/mips/bmips/dma.c

Purpose: BMIPS DMA range and remapping setup for device-tree-described Broadcom systems.

Important APIs and functions: architecture DMA setup code inspects DT DMA ranges and configures direct mapping offsets or fallbacks used by DMA API translations.

Control flow: early platform setup parses memory/DMA constraints before devices probe, then generic DMA mapping uses the established offsets.

State and persistence: boot-time DMA address policy only.

Dependencies and integration points: integrates devicetree, memblock, DMA direct mapping, and BMIPS device population.

Risks and test signals: bad DMA windows corrupt I/O or break devices above 32-bit address limits. Test network/storage DMA workloads and DT variants with different ranges.
