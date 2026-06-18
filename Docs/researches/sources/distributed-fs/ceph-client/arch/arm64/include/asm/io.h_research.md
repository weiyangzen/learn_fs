## sources/distributed-fs/ceph-client/arch/arm64/include/asm/io.h

Purpose: implements arm64 raw MMIO accessors, IO barriers, PCI IO space mapping, write-combining copy helpers, and ioremap variants.

Important APIs/types/functions: exports `__raw_read/write{b,w,l,q}`, IO barrier macros, `arch_has_dev_port`, `IO_SPACE_LIMIT`, `PCI_IOBASE`, optimized `__iowrite32_copy` and `__iowrite64_copy`, `ioremap_prot`, `ioremap`, `ioremap_wc`, `ioremap_np`, `ioremap_encrypted`, big-endian IO read/write macros, `ioremap_cache`, physical range validators, `arch_memremap_can_ram_remap`, and `arm64_is_protected_mmio`.

Control flow: raw accessors emit loads/stores, with alternative acquire loads for device-load errata. IO read barriers enforce DMA ordering and a control dependency. Constant-sized copy helpers emit contiguous stores and `dgh`; dynamic copies call full implementations. Mapping helpers select page attributes.

State and persistence: MMIO writes affect devices; ioremap creates persistent virtual mappings until unmapped; protected-MMIO checks query realm state.

Dependencies and integration: depends on barriers, memory layout, early_ioremap, alternatives, cpufeature, RSI/realm support, PCI, and generic IO.

Risks: ordering or attribute mistakes can corrupt devices, break PCI write combining, or map protected memory incorrectly. Test signals are driver MMIO tests, PCI write-combining throughput, ioremap debug, endian IO tests, and realm/protected-MMIO tests.
