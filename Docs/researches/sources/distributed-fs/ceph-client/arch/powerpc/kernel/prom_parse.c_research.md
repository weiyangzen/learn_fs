# sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_parse.c

## Purpose
This file provides a small helper for decoding Open Firmware DMA window properties into bus number, physical address, and size values.

## Important APIs, Types, And Functions
`of_parse_dma_window(struct device_node *dn, const __be32 *dma_window, unsigned long *busno, unsigned long *phys, unsigned long *size)` is the sole function. It uses `of_read_number()`, `of_get_property()`, `of_n_addr_cells()`, and `of_n_size_cells()`.

## Control Flow
The parser reads the first cell as `busno`, then determines the number of DMA address cells from `ibm,#dma-address-cells`, falling back to `#address-cells` and finally the node default. It reads the physical address, advances by that cell count, determines the DMA size cell count from `ibm,#dma-size-cells` or the normal size-cell default, and reads the size.

## State And Persistence
The function has no static state. It writes only through caller-provided output pointers.

## Dependencies And Integration Points
It integrates with OF/device-tree PCI and DMA code that consumes IBM DMA window properties. The includes indicate use alongside resource and Ethernet/Open Firmware address helpers, though this file itself only needs the OF cell-parsing path.

## Risks
The function trusts that `dma_window` contains enough cells for the chosen address and size widths. Incorrect cell-count properties or a malformed property can cause wrong decoding by the caller.

## Test Signals
Useful tests include device-tree fixtures with IBM-specific cell-count properties, generic `#address-cells`/`#size-cells` fallback, one-cell and two-cell addresses, and big-endian cell values.
