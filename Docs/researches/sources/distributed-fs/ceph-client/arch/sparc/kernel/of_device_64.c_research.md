# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_64.c

Purpose: Builds SPARC64 platform devices, resources, and IRQ mappings from the Open Firmware tree, with special handling for PCI, Simba, SBUS, and FHC/Central buses.

Important APIs/types/functions: `of_ioremap()`/`of_iounmap()` reserve/release resource ranges and return direct physical-address cookies as `__iomem` pointers. Bus translators include PCI, Simba, SBUS, FHC, and default entries. Resource helpers mirror SPARC32 but keep 64-bit addresses and mask hypervisor physical aliases. IRQ helpers include `apply_interrupt_map()`, `pci_irq_swizzle()`, `build_one_device_irq()`, and OF debug parsing. `scan_one_device()`, `scan_tree()`, and `scan_of_devices()` create devices.

Control flow: Postcore scanning creates a root platform device and recursively registers children. Resources are built from bus-specific address properties through parent `ranges`. IRQs are copied from `interrupts`, translated by direct node irq translators, interrupt-map properties, PCI swizzling, or ancestor translators, then assigned NUMA affinity when possible.

State and persistence: Persistent state consists of registered platform devices, resource arrays, translated IRQs, dev archdata, and optional resource/IRQ verbose flags from `of_debug=`.

Dependencies and integration points: It integrates OF property parsing, SPARC64 IRQ translator nodes, generic platform devices, PCI interrupt conventions, NUMA affinity, `tlb_type == hypervisor` address masking, and common bus helpers.

Risks and test signals: Interrupt-map parsing is sensitive to cell counts and masks; fallback PCI swizzling handles firmware gaps but can misroute unusual bridges. `of_ioremap()` only reserves regions rather than creating remapped virtual addresses. Tests include PCI with/without ranges, Simba bridges, FHC nodes, interrupt-map translation, onboard PCI controller fallback, NUMA IRQ affinity, too many IRQ/resource warnings, and hypervisor address masking.
