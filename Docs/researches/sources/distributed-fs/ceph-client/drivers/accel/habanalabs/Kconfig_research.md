# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Kconfig

Purpose: defines configuration for the HabanaLabs DRM accel driver and optional NVMe peer-to-peer direct I/O support.

Important entries: `DRM_ACCEL_HABANALABS` is a tristate depending on `DRM_ACCEL`, x86_64, PCI, and MMIO, selecting allocator, hwmon, dma-buf, CRC32, and firmware loader support. Nested `HL_HLDIO` enables HabanaLabs NVMe Direct I/O when PCI P2PDMA and block support are available.

Control flow: Kconfig determines whether the large HabanaLabs accelerator stack and optional HLDIO object are built.

State and persistence: build-time only; no runtime state.

Dependencies: DRM accel core, PCI, x86_64, HAS_IOMEM, firmware loading, DMA shared buffers, hwmon, CRC32, and optional P2PDMA/block.

Risks: HLDIO help notes hardware/IOMMU topology constraints; enabling it on unsupported systems may still compile but runtime paths must validate.

Test signals: config matrix for built-in/module/disabled, HLDIO enabled/disabled, dependency-disabled builds, and Kconfig help consistency with UAPI location.
