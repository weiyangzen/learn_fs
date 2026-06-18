# sources/distributed-fs/ceph-client/arch/powerpc/mm/init-common.c

Purpose: centralizes shared PowerPC MM initialization state, KUP boot toggles, and page-table slab cache setup.

Important APIs and control flow: early parameters `nosmep` and `nosmap` disable KUEP/KUAP. `setup_kup()` calls architecture implementations of KUAP and KUEP setup. `pgtable_cache_add()` creates zeroing slab caches for higher-level page tables and hugepage page tables, using order-specific constructors and alignment sufficient for RCU freeing metadata. `pgtable_cache_init()` installs caches needed by the configured page-table geometry.

State and dependencies: exported state includes `memstart_addr`, `kernstart_addr`, `kernstart_virt_addr`, `disable_kuep`, `disable_kuap`, optional KFENCE flags, and `pgtable_cache[]`. Dependencies include SMP boot CPU checks, KUP helpers, slab allocation, PGD/PMD/PUD cache index macros, and KVM HV consumers of page-table caches. Risks are misaligned cache allocations, missing constructor coverage if `MAX_PGTABLE_INDEX_SIZE` changes, boot-parameter weakening of protections, and incorrect setup order before allocations. Test signals include boot logs for KUP activation, KVM HV module load, page-table allocation stress, and nosmap/nosmep boot tests.
