# sources/distributed-fs/ceph-client/drivers/iommu/apple-dart.c

Purpose: Apple DART IOMMU driver for Apple Silicon SoCs. It probes DART MMIO blocks, maps device stream IDs from devicetree, creates IOMMU domains backed by `io-pgtable`, programs per-stream TCR/TTBR registers, handles faults, and supports suspend/resume.

Important APIs, types, and functions: the primary ops are `apple_dart_iommu_ops` and default domain ops for attach/map/unmap/TLB sync. Hardware description uses `struct apple_dart_hw`; device state uses `struct apple_dart`; domain state uses `struct apple_dart_domain`; device stream state uses `struct apple_dart_master_cfg` and stream maps. Key functions include `apple_dart_probe()`, `apple_dart_of_xlate()`, `apple_dart_finalize_domain()`, `apple_dart_attach_dev_paging()`, identity/blocked attach handlers, `apple_dart_domain_flush_tlb()`, and T8020/T8110 IRQ handlers.

Control flow: probe maps MMIO, enables clocks, reads parameters, validates stream count, resets hardware, registers IRQ and IOMMU device. `of_xlate` builds per-device stream maps and checks that all DARTs for a device share compatible page size/address size. Domain finalization allocates `io_pgtable_ops`, records aperture geometry, and snapshots stream maps. Paging attach adds streams atomically and writes TTBRs/TCRs; identity attach writes bypass TCRs; blocked attach disables DMA.

State and persistence: per-DART state includes MMIO base, clocks, stream count, capabilities, stream-to-group mapping, saved TCR/TTBR registers for PM, and an IOMMU core device. Domains retain atomic SID bitmaps because attach/detach can race. Hardware retains TCR/TTBR stream programming until reset, blocked attach, suspend/resume restore, or driver removal.

Dependencies and integration points: depends on devicetree IOMMU xlate, platform driver/probe, clocks, shared IRQs, `io-pgtable` formats `APPLE_DART`/`APPLE_DART2`, DMA-IOMMU reserved regions, PCI Apple MSI doorbell reserved region, and generic IOMMU grouping.

Risks: devices spanning multiple DARTs must have compatible geometry; `MAX_DARTS_PER_DEVICE` and static stream arrays encode platform assumptions. Flushes are whole-stream rather than fine-grained. Bypass may be unavailable or forced by page-size mismatch. Group merging for PCI assumes Apple PCIe devices from the same bus do not span multiple DARTs.

Test signals: devicetree xlate with one/multiple streams, map/unmap DMA through io-pgtable, identity/blocked domain switching, DART fault IRQ decoding, PM suspend/resume restoring TCR/TTBRs, PCI MSI doorbell reserved region, and probe/remove cleanup with clocks and shared IRQs.
