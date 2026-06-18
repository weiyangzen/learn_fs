# sources/distributed-fs/ceph-client/drivers/pci/iomap.c

## Purpose
Provides default PCI BAR mapping helpers that return `__iomem` cookies for MMIO or I/O port BARs, plus an architecture-gated default `pci_iounmap()`.

## Important APIs, Types, and Functions
Exported functions are `pci_iomap_range()`, `pci_iomap_wc_range()`, `pci_iomap()`, `pci_iomap_wc()`, and conditionally `pci_iounmap()`.

## Control Flow
Mapping validates the BAR index, reads BAR start/length/flags, rejects zero or out-of-range offsets, clamps to `maxlen`, then maps I/O resources through `__pci_ioport_map()` or memory resources through `ioremap()`/`ioremap_wc()`. WC mapping rejects I/O port BARs. The default unmap treats generic fixed I/O-port mappings under `PCI_IOBASE` as no-op and otherwise calls `iounmap()`.

## State and Persistence Behavior
The file creates virtual mappings but stores no state itself. Mapping lifetime is owned by callers and must be released with the appropriate unmap helper.

## Dependencies and Integration Points
Depends on PCI resource helpers, `pci_bar_index_is_valid()`, architecture I/O mapping support, and core I/O remap APIs. It is used broadly by PCI drivers and subsystems that map BARs.

## Risks
Callers must not request invalid offsets or forget unmap. WC mapping on device memory can change ordering semantics and must match device requirements. The default `pci_iounmap()` intentionally preserves legacy architecture behavior and may not fit architectures with unusual I/O-port mapping rules.

## Test Signals
Map MMIO, WC MMIO, and I/O BARs; reject invalid BARs, zero starts, and offsets beyond BAR length; clamp max length; unmap on generic and non-generic I/O mapping architectures.
