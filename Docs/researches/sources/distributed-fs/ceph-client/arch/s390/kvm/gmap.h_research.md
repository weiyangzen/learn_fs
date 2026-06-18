# sources/distributed-fs/ceph-client/arch/s390/kvm/gmap.h

## Purpose
Declares the s390 KVM guest address-space object and its public operations. It also provides inline predicates and exchange wrappers that add gmap-specific prefix, dirty, and vSIE shadow notification behavior around raw DAT table updates.

## Important APIs, Types, And Functions
`enum gmap_flags` defines shadow, ownership, ucontrol, huge-page, pfault, storage-key, CMMA, and export-on-unmap flags. `struct gmap` stores flags, EDAT level, invalidation state, owning KVM, ASCE, child/scb lists, parent, original guest ASCE for shadows, rmap radix tree, and refcount. Public declarations cover lifecycle, mapping, unmapping, dirty/age sync, ucontrol translation/map/unmap, storage keys, protected virtualization destroy, vSIE shadow creation/invalidation, rmap insertion/protection, CMMA dirty marking, and huge-page splitting.

Inline helpers include `uses_skeys`, `uses_cmm`, `pfault_enabled`, `is_ucontrol`, `is_shadow`, `owns_page_tables`, `gmap_get`, `gmap_put`, `gmap_handle_vsie_unshadow_event`, `gmap_mkold_prefix`, `gmap_unmap_prefix`, `_gmap_ptep_xchg`, `gmap_ptep_xchg`, `_gmap_crstep_xchg_atomic`, `gmap_crstep_xchg_atomic`, and `gmap_is_shadow_valid`.

## Control Flow
Callers use lifecycle APIs to allocate a root gmap or child shadow, then call `gmap_link` from the fault path to map host pages. Table-entry mutation should go through the inline wrappers rather than raw DAT helpers. These wrappers clear prefix/vSIE notification state, send prefix refresh or unshadow events when entries become invalid/protected, and mark pages dirty when dirty state transitions from clean to dirty.

## State And Persistence
The header defines all long-lived `struct gmap` fields and the flags that drive behavior in `gmap.c` and `gaccess.c`. Reference counting controls disposal. Child lists and rmap trees persist across faults so vSIE shadows can be reused until invalidated. No durable persistence is involved.

## Dependencies And Integration Points
Includes `dat.h` and depends on KVM locking, list, radix-tree, and refcount infrastructure. It is included by guest access, fault-in, diagnose/intercept-adjacent memory paths, and nested virtualization code. The inline exchange wrappers are the integration seam between raw DAT table operations and higher-level KVM events.

## Risks And Edge Cases
Bypassing gmap exchange wrappers can miss dirty marking, prefix refresh, or vSIE unshadow notifications. `gmap_put` assumes a valid nonzero refcount and disposes immediately at zero. Some wrappers require `kvm->mmu_lock` and may require or forbid `children_lock` depending on the `needs_lock` path. Shadow validity compares ASCE and EDAT level only; callers must also manage refcounts and invalidation races.

## Test Signals
Compile-time users should be checked for lockdep assertions. Runtime signals include dirty-bit transitions, prefix remapping tests, vSIE shadow invalidation, gmap refcount disposal, storage-key/CMMA paths, and ensuring all table mutations in new code go through the gmap wrappers.
