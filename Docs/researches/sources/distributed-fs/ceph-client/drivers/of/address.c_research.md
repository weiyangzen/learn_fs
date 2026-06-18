# sources/distributed-fs/ceph-client/drivers/of/address.c

Purpose: Core OF address translation and resource construction logic. It converts device-tree `reg`, `ranges`, `dma-ranges`, PCI/ISA address encodings, and MMIO/PIO resources into CPU physical addresses, DMA regions, and kernel `struct resource` objects.

Important APIs/types/functions: `struct of_bus` abstracts bus-specific cell counting, mapping, translation, and flag extraction. Exported APIs include `of_translate_address()`, `of_translate_dma_address()`, `of_translate_dma_region()`, `__of_get_address()`, `of_property_read_reg()`, `of_pci_range_parser_init()`, `of_pci_dma_range_parser_init()`, `of_pci_range_parser_one()`, `of_dma_get_range()`, `of_dma_get_max_cpu_address()`, `of_dma_is_coherent()`, `of_address_to_resource()`, `of_pci_address_to_resource()`, `of_iomap()`, and `of_io_request_and_map()`. `__of_address_resource_bounds()` is visible to KUnit and checks `struct resource` overflow.

Control flow: translation starts by matching the parent bus, counting address/size cells, copying the input address, then walking parent nodes. Each level chooses the parent bus, handles logical PIO host ranges, applies `ranges` or `dma-ranges` through `of_translate_one()`, and updates the address cells until root is reached. Resource conversion fetches the selected `reg` or PCI BAR address, translates memory or I/O space, applies optional nonposted MMIO flags, and fills bounded resource start/end.

State/persistence: no persistent mutable state except a static cached PowerMac empty-ranges quirk result. Parsers carry iteration state over property cell arrays. Mapping helpers create runtime ioremap mappings and resource reservations for callers.

Dependencies/integration: central dependency for platform bus probing, PCI host bridge resources, DMA setup, reserved/translated MMIO consumers, logic PIO, KUnit overflow tests, and architecture DMA coherency defaults. Conditional PCI and DMA sections compile based on `CONFIG_PCI` and `CONFIG_HAS_DMA`.

Risks: address-cell and size-cell validation is critical; bad DT properties return `OF_BAD_ADDR` or `-EINVAL`. Empty `ranges` semantics include historical PowerPC/Apple quirks and special `dma-ranges` handling. I/O space translation can fail if PCI I/O ranges are not registered early enough. DMA range parsing allocates a sentinel-terminated map and must skip untranslatable ranges. Overflow handling protects resource bounds but consumers must check return values.

Test signals: KUnit for `__of_address_resource_bounds()` overflow and zero-size behavior; DT tests for default, default-flags, ISA, and PCI bus mappings; missing versus empty `ranges`; `dma-ranges` ancestry and `interconnects` `dma-mem` parent selection; I/O port translation with logic PIO; nonposted MMIO flag propagation; and `of_iomap()`/`of_io_request_and_map()` success/failure paths.
