# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_64k.c

Purpose: Implements hash page-table fault insertion/update for 64K Linux base pages, including the special case where hardware uses 4K HPTEs inside a 64K software PTE. This is a low-level Book3S hash MMU path used after `hash_page_mm()` has found a present Linux PTE and selected the effective page size.

Important APIs and functions: `__hash_page_4K()` handles sub-4K hardware mappings for a Linux 64K page. `__hash_page_64K()` handles direct 64K HPTE insertion/update. `__rpte_sub_valid()` and `hpte_soft_invalid()` validate per-subpage hash slot metadata held in `real_pte_t`. Both hashing functions consume `mmu_hash_ops` callbacks for `hpte_insert`, `hpte_updatepp`, `hpte_remove`, and `hpte_invalidate`, and use helpers such as `htab_convert_pte_flags()`, `hash_page_do_lazy_icache()`, `pte_get_hash_gslot()`, `flush_hash_page()`, and `hpt_do_stress()`.

Control flow: Both paths first atomically set `H_PAGE_BUSY`, `_PAGE_ACCESSED`, and conditionally `_PAGE_DIRTY` with `pte_xchg()`, returning to the fault path on busy PTEs or permission mismatch. The 4K path applies subpage protection, computes the subpage index, invalidates a previous 64K HPTE when converting to combo mode, updates an existing subpage HPTE if valid, otherwise inserts into primary then secondary hash groups and evicts/retries on full groups. The 64K path refuses unsupported cache-inhibited large-page mappings, updates an existing HPTE if possible, or inserts a new 64K HPTE.

State and persistence: Persistent state lives in the Linux PTE bits: `H_PAGE_BUSY`, `H_PAGE_HASHPTE`, `H_PAGE_COMBO`, `_PAGE_HPTEFLAGS`, and packed hash slot indexes. The 4K path initializes invalid subpage slot metadata with `INVALID_RPTE_HIDX`. No disk state exists; persistence is CPU/MMU runtime state.

Dependencies and integration: Called from `hash_utils.c` through `hash_page_mm()` and `hash_preload()`. It depends on page-size definitions, VSID/VPN hashing, `mmu_hash_ops` backend registration from native/pseries/PS3 code, and PowerPC PTE flag layout constraints asserted during hash MMU init.

Risks: Incorrect busy-bit handling can deadlock faults. Slot encoding must avoid software-invalid values, especially secondary slot value `0xf`. Failed hypervisor insertion restores the old PTE but leaves the fault path responsible for SIGBUS/debug output. Conversions between 64K and 4K combo mappings require HPTE invalidation or stale translations remain.

Test signals: Exercise user faults on 64K kernels with normal, write, execute, cache-inhibited, and subpage-protected mappings. THP demotion and `stress_hpt` help expose hash collision retry paths. KUnit or fault-injection coverage should validate `__rpte_sub_valid()` and soft-invalid slot handling.
