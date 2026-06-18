# sources/distributed-fs/ceph-client/arch/sparc/lib/clear_page.S

Purpose: Baseline SPARC64 page clear and user-page clear implementation.

Important APIs/functions: Exports `_clear_page` and `clear_user_page`.

Control flow: Handles page clear through VIS/block store sequences, with cache/page-color considerations from SPARC headers. `clear_user_page` reaches common clear code after any needed setup, and the common loop writes zeros over `PAGE_SIZE`.

State and persistence: Mutates destination page only; uses transient VIS/FPU state.

Dependencies/integration: Includes `linux/pgtable.h`, `asm/visasm.h`, `asm/thread_info.h`, `asm/page.h`, `asm/spitfire.h`, and `asm/head.h`. CPU-specific page patchers may replace it.

Risks/test signals: VIS state and cache alias behavior are important. Test page clear correctness, user-page clear, CPU patch interaction, and FP/VIS state preservation.
