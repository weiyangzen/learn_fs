# sources/distributed-fs/ceph-client/arch/mips/include/asm/prefetch.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/prefetch.h

### Purpose
`prefetch.h` defines MIPS prefetch hint numbers and assembler convenience macros for optional `pref` instructions, while documenting CPU-specific limitations and errata.

### Important APIs, Types, And Functions
Hint macros include `Pref_Load`, `Pref_Store`, `Pref_LoadStreamed`, `Pref_StoreStreamed`, `Pref_LoadRetained`, `Pref_StoreRetained`, `Pref_WriteBackInvalidate`, and `Pref_PrepareForStore`. Assembler macros include `__pref`, `pref_load`, `pref_store`, `pref_load_streamed`, `pref_store_streamed`, `pref_load_retained`, `pref_store_retained`, `pref_wback_inv`, and `pref_prepare_for_store`.

### Control Flow
Assembler code expands a prefetch macro. If `CONFIG_CPU_HAS_PREFETCH` is enabled it emits `pref`; otherwise it emits nothing.

### State, Persistence, Dependencies, And Integration
The only state affected is CPU cache/prefetch behavior. There is no persistence. Integration is with hand-written MIPS assembly and performance-sensitive memory paths.

### Risks
Some MIPS CPUs implement hints as no-ops or have broken hints; enabling the wrong hint can waste cycles or trigger errata. These macros intentionally do not validate target CPU errata at each call site.

### Test Signals
Cross-build assembler users with and without prefetch support; benchmark copy/checksum/cache-sensitive paths on affected CPUs; run errata-sensitive platforms with prefetch disabled/enabled as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/prefetch.h -->
