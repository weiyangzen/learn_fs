<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pfn.h -->
# sources/distributed-fs/ceph-client/include/linux/pfn.h

## Purpose
Defines basic PFN/physical-address conversion and page-alignment macros.

## Important APIs, Types, And Functions
- `PFN_ALIGN(x)` rounds an address-like value up to a page boundary.
- `PFN_UP(x)` converts bytes/addresses to a page count rounded up.
- `PFN_DOWN(x)` converts bytes/addresses to a page frame number rounded down.
- `PFN_PHYS(x)` converts a PFN to `phys_addr_t`.
- `PHYS_PFN(x)` converts a physical address to an unsigned long PFN.

## Control Flow
There is no runtime control flow. These macros expand into shifts and masks using `PAGE_SIZE`, `PAGE_SHIFT`, and `PAGE_MASK`.

## State And Persistence
No state is stored. The macros are pure arithmetic but depend on architecture page-size constants and `phys_addr_t` width.

## Dependencies And Integration Points
Includes `<linux/types.h>` and integrates broadly with memory management, bootmem, device memory, page tables, DMA, and per-CPU allocator sizing.

## Risks And Edge Cases
Risks include overflow when aligning large values, truncation in `PHYS_PFN()` to unsigned long on platforms with wider physical addresses, using macros with signed values, and assuming page size is 4 KiB.

## Test Signals
Build across page sizes and physical-address widths, verify boundary conversions around page edges, test large physical addresses, and use sparse/compiler warnings to catch type truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pfn.h -->
