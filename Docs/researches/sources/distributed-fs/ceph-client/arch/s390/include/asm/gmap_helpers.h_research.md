# sources/distributed-fs/ceph-client/arch/s390/include/asm/gmap_helpers.h

Purpose: This small header declares helper entry points for KVM guest address-space mapping maintenance.

Important APIs/types/functions: `gmap_helper_zap_one_page()`, `gmap_helper_discard()`, `gmap_helper_disable_cow_sharing()`, and `gmap_helper_try_set_pte_unused()` are the exported helpers.

Control flow: KVM or guest-memory management code calls these helpers to zap one host virtual page, discard a range, disable copy-on-write sharing for a protected guest context, or opportunistically mark a PTE unused.

State and persistence: State lives in the target `mm_struct`, its gmap list, PTEs, and COW-sharing flags; the header declares operations that mutate those structures but stores nothing itself.

Dependencies and integration points: It integrates with s390 KVM gmap code, `mm_struct` context fields from `mmu.h`, page-table helpers, and protected virtualization memory-sharing restrictions.

Risks and test signals: Misuse can leave stale guest translations or shared pages where secure/protected guests require exclusivity. Tests should include protected guest startup, KSM/zeropage disable paths, discard/zap range handling, and mm teardown with active gmapped memory.
