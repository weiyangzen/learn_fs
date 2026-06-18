# sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci.h

Purpose: defines the CQHCI register map, descriptor bit fields, crypto capability/configuration layouts, host state, host operation hooks, and exported CQHCI API used by MMC host drivers.

Important APIs and types: key types are `struct cqhci_host`, `struct cqhci_host_ops`, `union cqhci_crypto_capabilities`, `union cqhci_crypto_cap_entry`, and `union cqhci_crypto_cfg_entry`. Public functions are `cqhci_irq`, `cqhci_init`, `cqhci_pltfm_init`, `cqhci_deactivate`, `cqhci_set_tran_desc`, `cqhci_suspend`, and `cqhci_resume`. Inline register accessors `cqhci_writel` and `cqhci_readl` delegate to host ops when present.

Control flow: host drivers allocate or map a `cqhci_host`, fill optional `ops`, call `cqhci_init`, forward CQHCI interrupt status to `cqhci_irq`, and use suspend/resume/deactivate helpers from their PM paths. The CQHCI core uses register/descriptor macros from this header to build task, link, transfer, DCMD, and crypto descriptors.

State and persistence: `struct cqhci_host` holds all in-memory CQHCI state: MMIO base, MMC host pointer, lock, RCA, queue depth, direct command slot, capabilities, quirks, enabled/activated/recovery flags, descriptor sizes and DMA bases, wait queue, per-slot table, and optional crypto metadata. Hardware persistence is only through MMIO registers defined here.

Dependencies and integration points: depends on Linux bitfield, bitops, spinlock, completion, waitqueue, IRQ return, and MMIO helpers. It is the common contract between CQHCI core, crypto support, and platform-specific MMC host drivers.

Risks: bitfield macros are low-level and assume caller-provided values already fit hardware limits. `cqhci_writel/readl` dereference `host->ops`, so hosts must provide a valid ops pointer even when no callbacks are used. Crypto unions depend on hardware-defined byte ordering and layout. Quirk flags and descriptor-size fields must stay synchronized with the core descriptor allocator.

Test signals: all CQHCI users compile against this header; runtime signals are successful CQHCI probe, register access via custom and default ops, 32-bit and 64-bit DMA descriptor operation, crypto and non-crypto builds, and suspend/resume paths using the inline suspend helper.
