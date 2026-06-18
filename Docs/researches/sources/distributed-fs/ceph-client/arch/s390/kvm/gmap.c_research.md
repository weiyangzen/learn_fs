# sources/distributed-fs/ceph-client/arch/s390/kvm/gmap.c

## Purpose
Implements s390 KVM guest address-space management. It allocates and disposes gmaps, links faulted host pages into guest DAT tables, handles aging/dirty logging/unmapping, supports ucontrol address-space mappings, enables storage keys, destroys protected-virtualization pages, and manages vSIE shadow gmaps and reverse mappings.

## Important APIs, Types, And Functions
Public functions include `gmap_new`, `gmap_new_child`, `gmap_set_limit`, `gmap_remove_child`, `gmap_dispose`, `s390_replace_asce`, `_gmap_unmap_prefix`, `gmap_age_gfn`, `gmap_unmap_gfn_range`, `gmap_sync_dirty_log`, `gmap_try_fixup_minor`, `gmap_link`, `gmap_ucas_translate`, `gmap_ucas_map`, `gmap_ucas_unmap`, `gmap_split_huge_pages`, `gmap_enable_skeys`, `gmap_pv_destroy_range`, `gmap_insert_rmap`, `gmap_protect_rmap`, `gmap_set_cmma_all_dirty`, `_gmap_handle_vsie_unshadow_event`, and `gmap_create_shadow`.

Important internal helpers are `gmap_limit_to_type`, `gmap_add_child`, `gmap_rmap_radix_tree_free`, young/dirty/unmap DAT-walk callbacks, `_gmap_link`, ucontrol mapping helpers, PV destroy callbacks, `gmap_unshadow_level`, `gmap_unshadow`, `gmap_find_shadow`, and top-level ASCE protection helpers.

## Control Flow
`gmap_new` allocates a CRST root sized from the requested limit and initializes the ASCE and lists. Fault handling first tries `gmap_try_fixup_minor` for already-linked pages where only invalid/protect bits need changing. Slow linking uses `gmap_link`, chooses a page-table or 1M large-page level, walks/allocates DAT tables, and atomically exchanges PTE/CRSTE entries. Aging and dirty logging walk ranges with `dat_walk_ops`, clear young or soft-dirty state, mark host pages dirty, and notify prefix/vSIE users as needed. Unmap walks clear entries and optionally exports secure pages.

Shadow-gmap creation searches existing children, allocates a shadow, protects the guest ASCE top-level pages via parent rmaps, and adds the shadow to the parent. Later parent entry changes call `_gmap_handle_vsie_unshadow_event`, which uses radix-tree rmaps to invalidate affected shadow levels or removes entire shadows when the source ASCE range changes.

## State And Persistence
Persistent runtime state lives in `struct gmap`: flags, ASCE, child/shadow lists, parent pointer, `guest_asce`, `edat_level`, `invalidated`, `host_to_rmap` radix tree, and refcount. DAT tables and PGSTE bits hold mapped PFNs, dirty/young/protection state, prefix notifications, vSIE notifications, storage-key/CMMA state, and ucontrol metadata. No filesystem state is persisted.

## Dependencies And Integration Points
Depends on `dat.h` table primitives, `faultin.h`, KVM memslots and MMU locks, s390 TLB flush/invalidation, UV protected-virtualization conversion/destroy helpers, gmap helper functions for host-mm discard/unused pages, and vSIE notifier callbacks. It is the central integration point between KVM core MMU invalidations, s390 guest translation, dirty logging, protected virtualization, and nested virtualization.

## Risks And Edge Cases
Lock ordering is critical: `kvm->mmu_lock`, child locks, host-to-rmap locks, and PGSTE locks are combined in several paths. ASCE replacement forbids segment-type roots to avoid stale host-to-guest radix pointers. Prefix pages cannot be aged or unmapped while a vCPU is in SIE without refresh notification. Dirty-log sync must preserve guest-visible protection semantics while marking host pages dirty. Shadow invalidation must not miss rmaps or leave children attached after parent removal. Huge-page decisions must respect memslot boundaries and PFN/GFN alignment.

## Test Signals
Useful signals include guest boot and memory stress, dirty-log migration tests, young/idle aging tests, memslot move/delete, huge-page backing and split tests, storage-key enablement, ucontrol mapping tests, protected-virtualization import/export/destroy tests, vSIE nested guest tests, MMU notifier race tests, and lockdep/KASAN/KCSAN runs under fault pressure.
