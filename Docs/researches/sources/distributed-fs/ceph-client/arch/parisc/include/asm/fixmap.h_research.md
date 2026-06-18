# sources/distributed-fs/ceph-client/arch/parisc/include/asm/fixmap.h

Purpose: defines PA-RISC fixed virtual mapping slots used for early boot, I/O, and architecture-specific permanent mappings.

Important APIs/types/functions: declares fixed-address indices, `FIXADDR_TOP`, `FIXADDR_SIZE`, `__fix_to_virt`, `__virt_to_fix`, and `set_fixmap` integration.

Control flow: early or low-level code selects a fixed slot, installs a PTE, uses the stable virtual address, and later clears or reuses the slot when appropriate.

State and persistence: fixmap PTEs persist in kernel page tables while active. Dependencies and integration: included by `pgtable.h` and early ioremap/memory setup.

Risks and test signals: overlapping or out-of-range slots corrupt fixed mappings. Test with boot-time fixmap assertions, early ioremap users, and page-table dumps.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
