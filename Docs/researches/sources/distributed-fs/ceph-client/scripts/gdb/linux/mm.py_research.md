# sources/distributed-fs/ceph-client/scripts/gdb/linux/mm.py

## Purpose
`mm.py` supplies architecture-specific memory translation helpers and GDB commands for PFN, physical address, virtual address, `struct page`, and KASAN-tag-aware conversions.

## Important APIs, Types, and Functions
`page_ops` chooses `x86_page_ops` or `aarch64_page_ops` and requires `CONFIG_SPARSEMEM_VMEMMAP`. Both implementations expose `pfn_valid()`, `pfn_to_page()`, `page_to_pfn()`, `virt_to_phys()`, `virt_to_page()`, `page_to_virt()`, `page_address()`, and `folio_address()`. Commands include `lx-pfn_to_page`, `lx-page_to_pfn`, `lx-page_address`, `lx-page_to_phys`, `lx-virt_to_phys`, `lx-virt_to_page`, `lx-sym_to_pfn`, and `lx-pfn_to_kaddr`.

## Control Flow
Each command parses a numeric argument, instantiates `page_ops().ops`, calls the relevant conversion, and prints a result. Architecture constructors read kernel layout symbols such as `page_offset_base`, `vmemmap_base`, `phys_base`, `mem_section`, `memstart_addr`, and arm64 `TCR_EL1`.

## State and Persistence Behavior
Conversion objects cache derived address-space constants during construction. The script does not mutate kernel state. Results are snapshots of current symbol/register state; KASAN tag reset logic affects arm64 address handling.

## Dependencies and Integration Points
`page_owner.py`, `slab.py`, `vmalloc.py`, and `kasan.py` depend on these helpers. Integration requires generated config constants, full debug info for `struct page` and `struct mem_section`, and architecture symbols.

## Risks and Test Signals
The code only supports x86_64 and arm64 sparse vmemmap kernels. Incorrect VA bits, KASAN mode, or page table layout constants will produce plausible but wrong addresses. Test conversion round trips, `pfn_valid()` over holes, arm64 tagged addresses, and known symbol-to-physical translations.
