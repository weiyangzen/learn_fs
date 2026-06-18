# sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-bits.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-bits.h

### Purpose
`pgtable-bits.h` defines the bit-level MIPS PTE ABI: software present/write/accessed/modified/special/soft-dirty flags, hardware EntryLo valid/dirty/global/cache flags, optional RIXI no-read/no-exec bits, PFN shifts, cache attribute encodings, and conversion to TLB EntryLo.

### Important APIs, Types, And Functions
The central type is `enum pgtable_bits`, whose layout changes by XPA, 36-bit MIPS32, R3K, or R4K-style TLB. Important macros are `_PAGE_PRESENT`, `_PAGE_WRITE`, `_PAGE_ACCESSED`, `_PAGE_MODIFIED`, `_PAGE_HUGE`, `_PAGE_SPECIAL`, `_PAGE_SOFT_DIRTY`, `_PAGE_NO_EXEC`, `_PAGE_NO_READ`, `_PAGE_GLOBAL`, `_PAGE_VALID`, `_PAGE_DIRTY`, `_CACHE_*`, `PFN_PTE_SHIFT`, `_PFN_MASK`, `__READABLE`, `__WRITEABLE`, and `_PAGE_CHG_MASK`. `pte_to_entrylo` is the key inline function.

### Control Flow
Most behavior is compile-time bit selection. When a PTE is written to the TLB, `pte_to_entrylo` shifts away software-only bits and, on RIXI-capable CPUs, rotates the no-read/no-exec bits into the hardware position expected by EntryLo.

### State, Persistence, Dependencies, And Integration
State is encoded in page-table words and later in CP0 EntryLo registers; there is no persistent storage. Dependencies are `CONFIG_*` CPU/MM options, `cpu_has_rixi`, `PAGE_SHIFT`, and cache-mode definitions. Integration is central to `pgtable.h`, TLB refill handlers, cacheability setup, soft-dirty tracking, special PTEs, huge pages, and memory-protection enforcement.

### Risks
Bit overlap is the main risk: a misplaced enum value can turn a software bit into a hardware permission or cache attribute. RIXI runtime handling depends on assembly fast paths matching this C helper. Cache mode defaults affect DMA coherency and memory ordering.

### Test Signals
Build and boot R3K, R4K, RIXI, XPA, 36-bit, soft-dirty, special-PTE, and hugepage configs. Run mprotect, exec/no-exec, read-inhibit, dirty/accessed-bit, soft-dirty, DMA cacheability, and TLB refill stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-bits.h -->
