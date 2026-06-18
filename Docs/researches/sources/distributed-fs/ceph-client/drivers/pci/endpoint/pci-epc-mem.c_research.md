<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-mem.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-mem.c

## Purpose
Implements address-space allocation for endpoint controller memory windows. EPF and EPC core code use it to reserve local physical ranges that can be mapped to host PCI addresses for outbound transfers or memory windows.

## Important APIs, Types, and Functions
`pci_epc_multi_mem_init()` initializes one or more `struct pci_epc_mem` windows with bitmaps and per-window locks. `pci_epc_mem_init()` is the single-window wrapper. `pci_epc_mem_exit()` frees all window metadata. `pci_epc_mem_alloc_addr()` finds a free aligned region, ioremaps it, and returns virtual and physical addresses. `pci_epc_mem_free_addr()` unmaps and releases the bitmap region. `pci_epc_mem_get_order()` computes bitmap allocation order using the controller window page size rather than `PAGE_SIZE`.

## Control Flow
Initialization normalizes each requested window page size to at least `PAGE_SIZE`, calculates page count and bitmap size, allocates metadata, and sets `epc->windows`, `epc->mem`, and `epc->num_windows`. Allocation scans all windows that can fit the requested size, aligns size to the window page size, locks the window bitmap, reserves a free region, calculates physical address, ioremaps the region, and returns it. Free finds the window containing the physical address, iounmaps, recalculates the bitmap order, and releases the region.

## State and Persistence
State is stored in `epc->windows[]`, each window's bitmap, page count, page size, physical base, and mutex. Allocated regions are not persisted; they must be explicitly freed by callers. `epc->num_windows` acts as the initialization flag.

## Dependencies and Integration Points
Depends on ioremap/iounmap, bitmap region helpers, mutexes, and `struct pci_epc`. It is used by EPC core `pci_epc_mem_map()` and endpoint function drivers such as vNTB to allocate local outbound-memory backing.

## Risks and Edge Cases
Window size smaller than page size produces zero pages and should be avoided by controller drivers. Allocation may fail in one window after reserving a bitmap region if `ioremap()` fails; the code releases that region and continues. Freeing an address outside all windows only logs an error and leaks nothing else, but it indicates caller state corruption. The allocator is first-fit by window and bitmap region, with no persistence or compaction beyond freeing regions.

## Test Signals
Initialize single and multiple windows, allocate/free varying sizes and page sizes, exhaust windows, force ioremap failure if possible, verify no bitmap leak after failed mapping, and exercise allocation through `pci_epc_mem_map()` loops in endpoint-test read/write/copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-mem.c -->
