<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_address.h -->
# sources/distributed-fs/ceph-client/include/linux/of_address.h

## Purpose
This header declares Devicetree address translation and resource extraction helpers for `reg`, `ranges`, `dma-ranges`, MMIO mapping, and PCI-style address windows.

## Important APIs, types, and functions
`struct of_pci_range_parser`/`of_range_parser` tracks parser state for range entries. `struct of_pci_range`/`of_range` holds bus, CPU, parent bus, size, and flags. `of_range_count()` reports remaining entries in an initialized parser. Translation APIs include `of_translate_address()`, `of_translate_dma_address()`, and `of_translate_dma_region()`. Resource and mapping helpers include `of_address_to_resource()`, `of_iomap()`, `of_io_request_and_map()`, `__of_get_address()`, `of_get_address()`, `of_get_pci_address()`, `of_property_read_reg()`, `of_pci_address_to_resource()`, `of_pci_range_to_resource()`, `of_range_to_resource()`, `of_address_count()`, and `of_dma_is_coherent()`.

## Control flow
Callers decode a node's address cells through `__of_get_address()` or `of_property_read_reg()`, translate them through parent `ranges` or `dma-ranges`, then convert the result into a Linux `struct resource` or ioremapped pointer. Range users initialize a parser and iterate with `for_each_of_pci_range()` until `of_pci_range_parser_one()` returns `NULL`. Disabled address support leaves translation unavailable, returning `OF_BAD_ADDR`, `NULL`, `IOMEM_ERR_PTR(-EINVAL)`, or negative errno.

## State and persistence
The parser stores iteration cursor state only. No persistent storage is owned here; persistent state is firmware-provided address cells and kernel resource mappings created by downstream callers.

## Dependencies and integration points
It integrates OF node/property decoding with the resource tree, I/O mapping, PCI host bridge windows, DMA configuration, and platform-device population. It depends on `linux/of.h`, `ioport.h`, `io.h`, and `CONFIG_OF_ADDRESS`/`CONFIG_OF`.

## Risks and test signals
Risks include wrong `#address-cells`/`#size-cells`, range parser cursor reuse causing wrong counts, malformed `reg` length, DMA-vs-CPU address confusion, resource flag loss, and leaked requested mappings. Test with nested buses, empty and multiple `ranges`, PCI BAR conversion, `dma-ranges`, non-coherent DMA nodes, `!CONFIG_OF_ADDRESS` builds, and `of_address_count()` on sparse `reg` lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_address.h -->
