<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/kasan_init.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/kasan_init.c

### Purpose
`kasan_init.c` builds LoongArch KASAN shadow-memory mappings for direct-map, vmalloc/KFENCE, and module ranges, and translates between memory and shadow addresses for multiple LoongArch virtual ranges.

### Important APIs, Types, And Functions
Important functions are `kasan_mem_to_shadow()`, `kasan_shadow_to_mem()`, `kasan_early_init()`, and `kasan_init()`. Internal helpers allocate and populate PGD/P4D/PUD/PMD/PTE levels: `kasan_alloc_zeroed_page()`, `kasan_*_offset()`, `kasan_*_populate()`, `kasan_map_populate()`, and `clear_pgds()`. Static state includes `kasan_pg_dir`.

### Control Flow
Early init checks PGDIR alignment. Full init verifies `KASAN_SHADOW_END` is usable for current VA bits, copies `swapper_pg_dir` into a temporary KASAN PGD, installs it in `LOONGARCH_CSR_PGDH`, clears existing KASAN PGDs, maps the full shadow to the early zero page, populates vmalloc/KFENCE shadow, populates shadow for every memblock memory range and module range, converts early shadow PTEs to read-only zero-page mappings, restores `swapper_pg_dir`, flushes TLBs, and enables generic KASAN.

### State, Persistence, And Dependencies
Persistent state is KASAN shadow page-table memory and `init_task.kasan_depth`. It depends on memblock, LoongArch segmented address ranges, `kasan_early_shadow_*` objects, `swapper_pg_dir`, CSR page-directory registers, generic KASAN, and TLB flushes.

### Integration Points
Generic KASAN instrumentation calls `kasan_mem_to_shadow()` and `kasan_shadow_to_mem()`. `init.c` and `pgtable.c` supply page-table roots and invalid tables. KFENCE and vmalloc ranges are shadowed during init.

### Risks
Shadow-offset math is architecture-specific and can warn/return `NULL` for unsupported ranges. Misdetecting folded page-table levels can reuse early shadow tables incorrectly. Temporarily switching `PGDH` and clearing PGDs must be paired with TLB flushes. Systems with too-small VA bits intentionally disable KASAN.

### Test Signals
Boot LoongArch KASAN configs across page-table levels and VA widths, run KASAN selftests, vmalloc/KFENCE/module shadow tests, and early boot memory-allocation fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/kasan_init.c -->
