# sources/distributed-fs/ceph-client/arch/s390/include/asm/kfence.h

Purpose: This header provides s390 KFENCE pool setup and guard-page protection hooks.

Important APIs/types/functions: `__kernel_map_pages()`, `arch_kfence_init_pool()`, `arch_kfence_test_address()`, and `kfence_protect_page()` are the relevant interfaces.

Control flow: During KFENCE initialization the pool is forced to 4K mappings with `set_memory_4k()`. Guard pages are protected or unprotected by toggling kernel page mappings for the corresponding page.

State and persistence: Persistent state is KFENCE pool page-table mapping granularity and per-page access permissions; the header holds no counters.

Dependencies and integration points: It integrates Linux KFENCE with s390 set-memory and page mapping operations.

Risks and test signals: Failure to split large mappings or protect guard pages weakens detection. Tests should include KFENCE boot, allocation/free sampling, guard-page fault detection, and configs with huge direct-map mappings.
