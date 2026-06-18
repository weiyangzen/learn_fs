# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_64.h

Purpose: provides 64-bit Book3S KVM helpers for nested guests, HPTE locking and decoding, page-size and TLBIE encodings, Linux PTE read/update, rmap locking, radix/HPT page-table lookup, transactional-memory checkpoint copying, and nestedv2 counters/hooks.

Important APIs/types/functions: `struct kvm_nested_guest` tracks L1/L2 ownership, LPIDs, shadow page tables, process table, radix mode, refcount, and TLB flush state. `struct rmap_nested` and `for_each_nest_rmap_safe()` encode nested rmaps. Key helpers include `try_lock_hpte`, `unlock_hpte`, `kvmppc_hpte_page_shifts`, `compute_tlbie_rb`, `hpte_rpn`, `hpte_is_writable`, `hpte_cache_flags_ok`, `kvmppc_read_update_linux_pte`, permission helpers, `lock_rmap`, `slot_is_aligned`, `is_vrma_hpte`, `set_dirty_bits*`, `sanitize_msr`, and checkpoint copy helpers.

Control flow: nested guest code allocates or looks up an L2 object, maps L1 guest real addresses to host real pages, serializes faults/TLB invalidations through `tlb_lock`, and records nested rmaps. HPTE update flow atomically locks HPTE dword 0, decodes page-size and permission fields, updates dirty/reference state, emits TLBIE operands, and unlocks with release ordering.

State and persistence: persistent state lives in nested guest objects, memslot rmap entries, HPT entries, radix page tables, dirty bitmaps, PACA shadow vcpu storage, and transactional-memory checkpoint arrays in `vcpu->arch`. Per-CPU flush masks and previous CPU arrays persist until nested guest release.

Dependencies and integration points: includes hash MMU, bitops, CPU feature checks, PPC opcode macros, and PTE walking. It is used by Book3S HV HPT/radix MMU code, nested virtualization, dirty logging, and pSeries hypercall implementations.

Risks: HPTE locking uses endian-aware load-reserve/store-conditional and must preserve big-endian HPT layout. Nested rmap encodes pointers and single-entry sentinel bits in one word, so alignment and nonzero LPID assumptions are critical. Page-size encoding differs across POWER generations, and wrong TLBIE operands can leave stale translations.

Test signals: run HPT and radix KVM selftests, nested guest boot/migration tests, hugepage and 64K page-size coverage, dirty-log aging tests, concurrent H_ENTER/H_REMOVE stress, TM guest tests, and lockdep/KCSAN coverage around rmap and HPTE update paths.
