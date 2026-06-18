# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_types.h

Purpose: selects the 32-bit x86 page-table type model and derives common page-directory size/mask constants.

Important APIs, types, and functions: includes `pgtable-3level_types.h` and defines `PMD_SIZE`/`PMD_MASK` when `CONFIG_X86_PAE` is enabled, otherwise includes `pgtable-2level_types.h`. Defines `pgtable_l5_enabled()` as `0`, `PGDIR_SIZE`, and `PGDIR_MASK`.

Control flow: no runtime code. Compile-time PAE selection determines type widths and table geometry.

State and persistence: no state is owned.

Dependencies and integration points: included by `pgtable_types.h` and `pgtable_32.h`; consumed by all 32-bit MM code that needs `PGDIR_*` and folded-level behavior.

Risks: `pgtable_l5_enabled()` must remain false on 32-bit. PAE selection changes not only geometry but atomic update requirements and swap encoding.

Test signals: 32-bit PAE and non-PAE builds, compile-time folding checks, direct-map setup, and page-table walking across PGD boundaries.
