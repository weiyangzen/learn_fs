# sources/distributed-fs/ceph-client/arch/s390/kvm/gaccess.c

## Purpose
Implements s390 KVM guest memory access and address translation. It translates logical, real, and absolute guest addresses, enforces low-address/DAT/storage-key protections, copies data with storage keys, performs keyed guest cmpxchg, manages IPTE locking, and resolves vSIE shadow gmap faults.

## Important APIs, Types, And Functions
Exported functions include `ipte_lock_held`, `ipte_lock`, `ipte_unlock`, `access_guest_abs_with_key`, `access_guest_with_key`, `access_guest_real`, `cmpxchg_guest_abs_with_key`, `guest_translate_address_with_key`, `check_gva_range`, `check_gpa_range`, `kvm_s390_check_low_addr_prot_real`, and `gaccess_shadow_fault`.

Important internal structures are `union dat_table_entry`, `struct pgtwalk`, `union raddress`, `union alet`, `union ald`, `struct ale`, `struct aste`, `union oac`, `struct acc_page_key_context`, and `struct cmpxchg_key_context`. Key helpers are `ar_translation`, `get_vcpu_asce`, `guest_translate_gva`, `guest_range_to_gpas`, `vcpu_check_access_key_gpa`, `mvcos_key`, `__cmpxchg_with_key`, `walk_guest_tables`, `_gaccess_do_shadow`, `_do_shadow_pte`, and `_do_shadow_crste`.

## Control Flow
Normal guest access starts by reducing a logical address according to PSW addressing mode and obtaining the active ASCE from primary, secondary, home, real, or access-register space. DAT translation walks region/segment/page tables, checks EDAT large-page formats, DAT protection, instruction-execution protection, and memslot availability. `guest_range_to_gpas` splits a range by page fragments, checks low-address protection and storage keys, and optionally returns GPAs. `access_guest_with_key` holds the IPTE lock for DAT accesses, translates all fragments before copying, then copies each page with `mvcos` and the requested key, with fetch/storage protection override handling. Real and absolute helpers bypass parts of that translation as their names imply.

`cmpxchg_guest_abs_with_key` faults in the target page for write and executes the architecture keyed compare-and-swap helper for 1, 2, 4, 8, or 16 bytes. The vSIE path pins guest page-table pages with `walk_guest_tables`, protects parent mappings with rmap notifications, allocates or splits DAT tables, installs read-protected parent entries, and creates the corresponding shadow mapping.

## State And Persistence
The file mutates vCPU program-interruption state (`vcpu->arch.pgm`), SCA IPTE lock fields, `kvm->arch.ipte_lock_count`, gmap mappings, shadow-gmap rmaps, PGSTE `vsie_notif` bits, and pinned fault arrays. Watchpoint/copy/cmpxchg buffers are caller-owned. No durable state is stored.

## Dependencies And Integration Points
Depends on s390 PSW/control-register formats, access-register translation, DAT bit definitions, storage-key helpers from `dat.h`, gmap and shadow-gmap APIs, fault-in helpers, KVM memslots, lowcore access, and architecture instructions such as `mvcos` and keyed cmpxchg. It is used by instruction emulation, diagnose handling, intercept handling, guest debug, STHYI, MVPG partial execution, and vSIE.

## Risks And Edge Cases
Translation exception details are ABI-visible and must set TEID/access-id fields precisely. IPTE locking differs depending on SIIF availability and must synchronize against guest invalidations. Address wrap/truncation for 24-, 31-, and 64-bit modes matters when ranges cross page boundaries. Hardware-key copy may partially fail only after all software translation checks were done. Fetch/storage protection overrides are narrow and instruction dependent. vSIE shadowing is race-prone: pinned pages must be retried after MMU invalidation, parent-child locks must nest correctly, and stale shadows must be invalidated when protected parent entries change.

## Test Signals
Run s390 KVM guest-access selftests and instruction-emulation tests covering primary/secondary/home/access-register spaces, DAT off/on, low-address protection, storage-key match/mismatch, fetch and storage protection override, IEP, range wrapping, real/absolute helpers, keyed cmpxchg sizes/alignment, MVPG, STHYI, guest debug instruction fetches, and vSIE nested guests with table invalidation races.
