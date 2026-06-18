# sources/distributed-fs/ceph-client/lib/iomap.c

Purpose: provides the generic default implementation of the Linux `ioread*()`, `iowrite*()`, repeated I/O, I/O-port mapping, and PCI unmap helpers when an architecture does not provide its own version. The key abstraction is that a `void __iomem *` cookie may represent either MMIO or encoded PIO; `IO_COND()` decodes low cookie values as PIO and higher values as MMIO.

Important APIs: `ioread8/16/16be/32/32be`, 64-bit `__ioread64_*` variants on 64-bit builds, `iowrite8/16/16be/32/32be`, 64-bit `__iowrite64_*`, `ioread*_rep`, `iowrite*_rep`, `ioport_map`, `ioport_unmap`, and `pci_iounmap`. Internal helpers include PIO big-endian fallbacks, split-order 64-bit PIO reads/writes, raw MMIO repeated access loops, and `bad_io_access()` warning throttling.

Control flow: each scalar access calls `IO_COND()`, which either executes PIO instructions (`inb`, `outw`, etc.), MMIO accessors (`readl`, `writeq`, etc.), or emits a bounded warning and returns all-ones for bad reads. Repeated accessors use string I/O for PIO and raw loops for MMIO. Mapping encodes I/O ports as `port + PIO_OFFSET`; unmapping is a no-op for PIO and calls `iounmap()` for MMIO in PCI builds.

State and persistence: state is limited to the static warning counter in `bad_io_access()`. KMSAN integration marks hardware-read data initialized and checks data being written to devices.

Dependencies and integration: depends on `linux/io.h`, PCI support, KMSAN helpers, endian byte swaps, and architecture-provided overrides via preprocessor guards. It is exported for drivers and bus code.

Risks: incorrect cookie ranges can misclassify PIO/MMIO; repeated raw MMIO deliberately lacks barriers and byte-order conversion; 64-bit split access ordering must match device semantics; KMSAN count arithmetic must match element width.

Test signals: build coverage across `CONFIG_64BIT`, `CONFIG_HAS_IOPORT_MAP`, and `CONFIG_PCI`; driver smoke tests for PIO/MMIO devices; KMSAN checks for initialized reads and uninitialized writes; sparse `__iomem` diagnostics.
