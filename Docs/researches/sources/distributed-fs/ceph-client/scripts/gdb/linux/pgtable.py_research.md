# sources/distributed-fs/ceph-client/scripts/gdb/linux/pgtable.py

## Purpose
`pgtable.py` registers `translate-vm`, an x86 page-table walker that decodes CR3 and the hierarchy entries used to translate a virtual address.

## Important APIs, Types, and Functions
`Cr3` decodes CR3 flags and the root physical address. `PageHierarchyEntry` reads an eight-byte entry, decodes present/RW/user/cache/accessed/dirty/PAT/global/page-size/protection-key/NX bits, and computes either a page physical address or next-level address. `entry_va()` maps physical page-table addresses into the direct map.

## Control Flow
`TranslateVM.invoke()` parses the virtual address, reads `$cr3` and `$cr4`, chooses four or five levels from LA57, prints CR3 information, then repeatedly prints each page hierarchy entry until a leaf or non-present entry.

## State and Persistence Behavior
Read-only. It reads live registers and memory at invocation time; no persistent state survives the command.

## Dependencies and Integration Points
It depends on x86 paging layout, `page_offset_base`, target memory access, and little-endian entry reads. It is loaded by `vmlinux-gdb.py`.

## Risks and Test Signals
The tool is x86-only and uses a narrow `PHYSICAL_ADDRESS_MASK` expression that may not match every CPU physical-address width. It does not handle userspace CR3 PCID masking beyond the current masks. Test with known kernel/user mappings, huge pages, non-present entries, and LA57 kernels.
