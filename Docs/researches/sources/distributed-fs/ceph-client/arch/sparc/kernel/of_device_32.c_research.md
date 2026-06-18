# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_32.c

Purpose: Builds SPARC32 platform devices and resources from the Open Firmware tree, with translators for PCI, SBUS, AMBAPP, and default buses.

Important APIs/types/functions: Bus translators are represented by `struct of_bus` entries for PCI, SBUS, AMBAPP, and default mappings. Helpers include `of_bus_pci_match()`, `of_bus_pci_map()`, `of_bus_pci_get_flags()`, AMBAPP cell/map/flag helpers, `of_match_bus()`, `build_one_resource()`, `use_1to1_mapping()`, `build_device_resources()`, `scan_one_device()`, `scan_tree()`, and `scan_of_devices()`.

Control flow: A postcore initcall scans the root node and recursively creates platform devices. Each device inherits OF node identity, IRQs from `intr` or `interrupts` translated through `sparc_config.build_device_irq`, resources built by walking parent `ranges`, DMA masks, parent links, and platform bus type before `of_device_register()`.

State and persistence: The scan creates persistent `platform_device` objects and fills `dev_archdata.resource` and IRQ arrays. `of_resource_verbose` is set by `of_debug=1` for boot-time diagnostics.

Dependencies and integration points: It depends on OF property APIs, common address helpers from `of_device_common.c`, SPARC32 PROM IRQ formats, LEON AMBAPP support, platform bus registration, and `sparc_config` IRQ mapping callbacks.

Risks and test signals: Resource truncation to 32 bits and fixed resource arrays can misrepresent large or numerous regions. Missing `ranges` may force 1:1 mappings except for known hierarchy nodes. Tests include SPARC32 OF scanning on SBUS/PCI/LEON AMBAPP, `intr` versus `interrupts` properties, verbose resource output, devices with missing `ranges`, and registration failure cleanup.
