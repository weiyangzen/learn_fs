<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/dma.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/dma.h

Purpose: selects SH-4A DMAC base addresses and IRQ numbers for supported CPU subtypes.

Important APIs/types/functions: `DMTE*_IRQ`, `DMAE*_IRQ`, `SH_DMAC_BASE0`, and optional `SH_DMAC_BASE1` guarded by subtype config.

Control flow: DMAC platform code includes this header and instantiates channels from the chosen constants.

State and persistence: no software state; it describes fixed interrupt and MMIO topology.

Dependencies/integration: depends on `CONFIG_CPU_SUBTYPE_*` and feeds SH DMA engine registration.

Risks: subtype guard mistakes misroute DMA completion/error interrupts or point at the wrong controller bank.

Test signals: build every enabled subtype and test DMA memcpy/peripheral transfers plus error IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/dma.h -->
