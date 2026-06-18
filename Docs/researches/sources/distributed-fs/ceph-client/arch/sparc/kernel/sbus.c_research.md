# sources/distributed-fs/ceph-client/arch/sparc/kernel/sbus.c

Purpose: initializes UltraSPARC SYSIO/SBUS controller support: 64-bit DVMA slot configuration, SYSIO IRQ construction, ECC/SBUS error interrupt handlers, IOMMU and streaming-buffer setup, Starfire hookup, and OF archdata propagation.

Important APIs/functions: exported API is `sbus_set_sbus64()`. Internal flow uses `sbus_build_irq()`, `sysio_ue_handler()`, `sysio_ce_handler()`, `sysio_sbus_error_handler()`, `sysio_register_error_handlers()`, `sbus_iommu_init()`, and `sbus_init()`.

Control flow: `sbus_init()` iterates OF `sbus` nodes, finds platform devices, initializes SYSIO IOMMU/streaming-buffer state, and propagates archdata. IOMMU init maps controller registers from `reg`, allocates `iommu` and `strbuf`, programs TSB/control registers, clears diagnostic entries, installs the page table, enables streaming buffer and DVMA arbitration, optionally hooks Starfire, then registers UE/CE/SBUS error IRQs and enables ECC/error bits. Error handlers read AFSR/AFAR, clear primary/secondary bits, and print decoded fault details.

State and persistence: attaches `iommu`, `strbuf`, and NUMA archdata to SBUS platform devices; programs hardware registers; stores streaming-buffer flush flag addresses. State is runtime hardware state only.

Dependencies and integration points: depends on OF/platform devices, UPA register access, SPARC IRQ builder, IOMMU common allocation/table code, DMA burst flags, Starfire support, NUMA metadata, and `of_propagate_archdata()` for child devices.

Risks: SYSIO register offsets and INO mapping are fixed hardware contracts. Bad allocation or missing `reg` data is fatal during boot. Error IRQ registration failures halt the machine. `sbus_set_sbus64()` depends on slot-specific config offsets and silently returns for unsupported slots.

Test signals: SBUS boot/probe, child devices receiving IOMMU archdata, SBUS DMA including 64-bit DVMA burst configuration, UE/CE/SBUS error IRQ delivery and logs, Starfire platform hookup, and clean initcall behavior with multiple SBUS nodes.
