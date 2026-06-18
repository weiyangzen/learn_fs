# sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu.h

Purpose: This header defines the s390 `mm_context_t` fields used for address-space control, TLB flushing, guest mappings, protected guest tracking, and COW-sharing policy.

Important APIs/types/functions: `mm_context_t` contains a lock, attached CPU mask, flush counter and flag, gmap list and ASCE, active ASCE and limit, VDSO base, protected-count, and `allow_cow_sharing`. `INIT_MM_CONTEXT` initializes lock and gmap list for `init_mm`.

Control flow: MM creation initializes this context, switch code loads ASCEs from it, TLB flush paths coordinate via counters and CPU masks, and KVM gmap/protected-guest code tracks guest mappings and sharing restrictions.

State and persistence: Persistent state is per-mm and lives for the lifetime of the address space. The `protected_count` and COW-sharing bit directly affect page-table behavior in `pgtable.h` and gmap helpers.

Dependencies and integration points: It depends on cpumasks, errno, exception-table support, and s390 ASCE/page-table code, integrating memory management, KVM, TLB flush, VDSO, and protected virtualization.

Risks and test signals: Incorrect ASCE limits or protected counts can break address translation or secure guest isolation. Tests should include exec/fork, ASCE upgrade, context switch, KVM gmap use, protected guests, and TLB shootdowns.
