# sources/distributed-fs/ceph-client/arch/parisc/lib/iomap.c

Purpose: implements PA-RISC `iomap` accessors for generic drivers that use `ioread*`, `iowrite*`, repeat I/O, `ioport_map`, `ioport_unmap`, and `pci_iounmap`. It separates directly dereferenceable I/O memory from encoded indirect addresses by testing the top address bit and selecting an operation table region.

Important APIs/types/functions: `struct iomap_ops` contains function pointers for byte/word/dword and 64-bit reads/writes plus repeat operations. `ioport_ops` maps encoded port addresses through `inb/inw/inl`, `outb/outw/outl`, and `ins*/outs*`; `iomem_ops` maps legacy memory I/O through `read*`, `write*`, and raw big-endian forms. Exported symbols are the public integration surface.

Control flow: each exported accessor checks `INDIRECT_ADDR(addr)`. Indirect addresses dispatch through `iomap_ops[ADDR_TO_REGION(addr)]`; direct addresses are loaded/stored in place with little-endian conversion for non-`be` variants. Repeat forms loop over fixed-width elements for direct memory and delegate to port/memory repeat callbacks for indirect space. `ioport_map()` builds a region-8 encoded pointer; unmap functions call `iounmap()` only for non-indirect mappings.

State and dependencies: no persistent state beyond the static `iomap_ops[8]` dispatch table. Depends on PA-RISC address-region layout, `asm/io.h`, PCI optional build state, and 32-bit versus 64-bit address constants.

Risks: only regions 0 and 7 are populated, so an encoded pointer in another region would dereference a null ops table. Correctness is highly dependent on endian expectations, raw accessors, and address encoding. Repeat direct paths do not include explicit barriers beyond the underlying memory operations.

Test signals: PA-RISC build coverage for 32/64-bit, driver smoke tests using port and memory BAR access, endian-sensitive MMIO register tests, and PCI unmap tests for both encoded ports and true `ioremap()` pointers.
