# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.c

Purpose: supplies the D71/D32/Linlon D6 chip backend for Komeda: identification, IRQ decoding, resource enumeration, format table initialization, opmode changes, flushes, reset, and optional TBU/IOMMU connection.

Important APIs/types/functions: `d71_identify()` returns `d71_chip_funcs`; `d71_read_block_header()` and `d71_enum_resources()` enumerate hardware; `d71_irq_handler()` maps GCU/LPU/CU/DOU status to `komeda_events`; `d71_enable_irq()`, `d71_disable_irq()`, `d71_change_opmode()`, `d71_flush()`, `d71_connect_iommu()`, and `d71_disconnect_iommu()` implement chip hooks.

Control flow: probe reads core ID, validates product, resets GCU, discovers pipeline count and configuration either from legacy PERIPH or GCU config registers, creates generic Komeda pipelines, then scans fixed-size blocks and delegates to `d71_probe_block()`. Runtime PM resume enables IRQs and connects TBU; suspend disconnects TBU, disables IRQs, and clocks are handled by core device code. IRQ handling reads `GLB_IRQ_STATUS`, clears raw IRQ registers, translates block status bits, and resets sticky error bits.

State and persistence: `struct d71_dev` is stored in `mdev->chip_data` and holds MMIO sub-block addresses, capability bits, global scaler coefficient addresses, and D71 pipeline wrappers. Hardware state includes GCU opmode, config-valid flush bits, IRQ masks, and TBU control.

Dependencies/integration: integrates with `komeda_dev_funcs`, `komeda_pipeline_add()`, D71 component probing, DRM format capabilities, `malidp_io`, and runtime PM.

Risks: block scan assumes fixed 0x200 spacing and valid `num_blocks`. IRQ masks omit some events unless vblank is toggled separately. TBU wait timeouts are hardware-sensitive. Product IDs all share D71 funcs, so subtle D32/D6 differences depend on config probing. Test signals: probe on each compatible, suspend/resume, IRQ/vblank/flip/error events, IOMMU on/off paths, reset timeout behavior, and format-modifier validation.
