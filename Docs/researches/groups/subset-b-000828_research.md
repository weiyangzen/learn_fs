# subset-b-000828 Research

Grouped research report for the requested s390 KVM Ceph-client kernel subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/dat.h -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/dat.h

## Purpose
Defines the s390 KVM guest dynamic-address-translation table model used by the newer gmap code. It provides typed overlays for guest page-table entries, CRST entries, page-table adjunct PGSTEs, storage keys, ASCE helpers, DAT walkers, guest-fault descriptors, vSIE reverse mappings, and a small MMU allocation cache.

## Important APIs, Types, And Functions
Core exported types are `union pte`, `union pgste`, `union pmd`, `union pud`, `union p4d`, `union pgd`, `union crste`, `union skey`, `struct crst_table`, `struct page_table`, `struct dat_walk`, `struct dat_walk_ops`, `struct kvm_s390_mmu_cache`, `struct guest_fault`, and `struct vsie_rmap`. Entry constructors include `_pte`, `_crste_fc0`, `_crste_fc1`, token constructors such as `_CRSTE_HOLE`, `_CRSTE_EMPTY`, and `_PTE_EMPTY`, and ucontrol page-table-value helpers `PTVAL_PGT_ADDR` and `PTVAL_VMADDR`.

The header declares the implementation hooks used by `gmap.c`, `gaccess.c`, and `faultin.c`: `dat_entry_walk`, `_dat_walk_gfn_range`, `dat_set_asce_limit`, `dat_set_slot`, storage-key operations, CMMA/ESSA helpers, `dat_ptep_xchg`, `dat_crstep_xchg`, `dat_crstep_xchg_atomic`, `dat_free_level`, `dat_alloc_crst_sleepable`, and `kvm_s390_mmu_cache_topup`. Inline helpers cover ASCE sizing, table dereference, CRSTE/PTE origin extraction, large-page translation, pgste locking, IDTE/CRDTE invalidation, and MMU cache allocation/free.

## Control Flow
Callers usually start with an ASCE and a guest frame number. `dat_entry_walk` locates or creates the requested table level using flags such as `DAT_WALK_ALLOC`, `DAT_WALK_SPLIT`, `DAT_WALK_LEAF`, and `DAT_WALK_USES_SKEYS`. Mutations pass through `dat_ptep_xchg` or CRSTE exchange wrappers, which update table entries while preserving s390 invalidation and optional storage-key behavior. Higher-level users allocate from `struct kvm_s390_mmu_cache` first and fall back to atomic GFP allocations only when a cache is empty.

## State And Persistence
State is in-memory KVM MMU state: guest DAT tables, PGSTEs, storage-key bits, CMMA soft state, notification flags, and cached allocations. No filesystem state is persisted. PGSTE fields such as PCL, usage, CMMA dirty, prefix notification, and vSIE notification are intentionally persistent across individual faults until later aging, unmap, dirty-log, or shadow invalidation paths consume them.

## Dependencies And Integration Points
Depends on Linux KVM core types, radix trees, refcounts, page allocation, `asm/dat-bits.h`, `asm/tlbflush.h`, and s390 low-level instructions such as `idte`, `crdte`, and `cspg`. It is the shared contract for `gmap.c` guest address spaces, `gaccess.c` guest access and vSIE shadow faults, `faultin.c` host-page fault resolution, and s390 storage-key/CMMA emulation.

## Risks And Edge Cases
Bitfield layout must match s390 hardware formats exactly. PGSTE PCL locking is spin-based and correctness-sensitive. Wrong invalidation scope can leave stale guest translations. Large-page helpers return sentinel values on non-large entries, so callers must check leaf/table type. `gmap` notification flags embedded in entries must be cleared or propagated correctly to avoid stale prefix mappings or vSIE shadows. Allocation helpers use atomic/accounted GFP flags and can fail in fault paths, requiring callers to top up caches and retry.

## Test Signals
Useful signals include s390 KVM boot tests, guest memory fault tests, storage-key tests, CMMA/ESSA tests, dirty-log and aging tests, huge-page mapping/splitting tests, ucontrol tests, vSIE nested virtualization tests, protected-virtualization teardown tests, and lockdep/KCSAN coverage for pgste and mmu-lock interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/dat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/diag.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/diag.c

## Purpose
Implements in-kernel handling for selected s390 DIAGNOSE instructions intercepted by SIE. The handled diagnose codes cover page discard, time-slice yield, directed yield, page-reference services for pfault, IPL reset requests, and virtio-ccw hypercalls.

## Important APIs, Types, And Functions
The public entry point is `kvm_s390_handle_diag`. Internal handlers are `diag_release_pages`, `__diag_page_ref_service`, `__diag_time_slice_end`, `__diag_time_slice_end_directed`, `__diag_ipl_functions`, and `__diag_virtio_hypercall`. `do_discard_gfn_range` walks memslots and calls `gmap_helper_discard`. `diag9c_forwarding_overrun` rate-limits directed-yield forwarding through `diag9c_forwarding_hz`.

## Control Flow
`kvm_s390_handle_diag` rejects problem-state diagnose instructions, extracts the diagnose code, traces it, and dispatches by code. DIAG 0x10 validates a page-aligned real range, accounts for prefix-page remapping, locks the VM mmap for read, and discards matching host virtual ranges. DIAG 0x258 reads a real-address parameter block, validates version/length/masks, and either registers or cancels pfault token state. DIAG 0x44 yields the current vCPU. DIAG 0x9c attempts directed yield to a target vCPU or forwards to a preempted host CPU within a rate limit. DIAG 0x308 prepares reset flags and exits to userspace. DIAG 0x500 writes a virtio-ccw notification to the KVM I/O bus and returns the cookie/result in GPR2 when handled in-kernel.

## State And Persistence
State changes are runtime-only. The file updates vCPU statistics, trace events, `vcpu->arch.pfault_token/select/compare`, `run->s390_reset_flags`, `run->exit_reason`, and GPR return values. Static `forward_cnt` and `cur_slice` rate-limit DIAG 0x9c forwarding. Page discard affects host memory backing and guest page cache residency, not durable storage.

## Dependencies And Integration Points
Integrates with KVM memslot iteration, `gmap_helper_discard`, guest real-memory access helpers from `gaccess.h`, pfault state in `kvm-s390.h`, scheduler yield helpers, reset exit ABI (`KVM_EXIT_S390_RESET`), virtio-ccw notification bus, and s390 tracing/statistics. It is reached from the instruction-intercept dispatcher in `intercept.c`.

## Risks And Edge Cases
DIAG 0x10 must split ranges that overlap the two prefix pages or it can discard the wrong guest frames. The pfault token path must refuse token changes while a handshake is active and must distinguish specification from addressing exceptions. Directed yield has concurrency races with target vCPU scheduling and deliberately treats invalid/self/running targets as ignored. Reset handling returns `-EREMOTE` to force userspace action. Virtio hypercalls must not overwrite GPR2 if userspace will handle the diagnose.

## Test Signals
Exercise diagnose instruction emulation in s390 KVM selftests or guest workloads: page-release ranges including prefix overlap, pfault token/cancel return codes, spin/yield behavior, DIAG 0x308 reset exits and flags, virtio-ccw notifications with and without CSS support, problem-state privilege exceptions, and unknown diagnose fallback to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.c

## Purpose
Resolves guest frame faults into host PFNs and links them into the s390 gmap. It centralizes the slow path that faults host userspace memory in, handles async pfault setup, coordinates with KVM MMU invalidation sequencing, and releases pinned pages correctly.

## Important APIs, Types, And Functions
Exports `kvm_s390_faultin_gfn` and `kvm_s390_get_guest_page`. It uses `struct guest_fault` from `dat.h`, `gmap_try_fixup_minor`, `gmap_link`, `kvm_s390_new_mmu_cache`, `kvm_s390_mmu_cache_topup`, `__kvm_faultin_pfn`, `kvm_release_faultin_page`, `mmu_invalidate_retry_gfn_unsafe`, and `mmu_invalidate_retry_gfn`. It calls architecture async-page-fault setup via `kvm_arch_setup_async_pf`.

## Control Flow
`kvm_s390_faultin_gfn` first attempts a minor gmap fixup under `kvm->mmu_lock` read lock. If that fails, it repeatedly faults the GFN through the appropriate memslot, optionally using `FOLL_NOWAIT` for pfault attempts. `KVM_PFN_ERR_NEEDS_IO` either establishes async pfault for a vCPU or falls back to synchronous faulting. Addressing, signal, read-only, and generic error PFNs are converted to guest exception or kernel error returns. Once a PFN is available, the function checks invalidation sequence races, links the mapping under `mmu_lock`, releases the faulted page with the right dirty/error semantics, tops up the MMU cache on `-ENOMEM`, and retries on `-EAGAIN`.

`kvm_s390_get_guest_page` is a lighter helper that faults and pins a page for explicit users such as shadow-table walks without linking it into the gmap.

## State And Persistence
State is transient fault state in `struct guest_fault`: `gfn`, `pfn`, `page`, `writable`, `write_attempt`, `attempt_pfault`, `valid`, and optional callback/private data. The function mutates the VM gmap by calling `gmap_link`; it also updates vCPU pfault statistics. No durable persistence is involved.

## Dependencies And Integration Points
Depends on KVM memslots, SRCU protection, KVM MMU invalidation sequence barriers, s390 gmap mapping code, async pfault support, and page-release accounting. It is used by ordinary DAT fault handling, absolute guest access helpers, atomic guest cmpxchg, and vSIE shadow construction.

## Risks And Edge Cases
The caller must hold `kvm->srcu` and must not hold the mm lock. Missing invalidation retries can link stale PFNs. Page release must match whether the page was consumed, dirtied, or abandoned. Async pfault is only valid for vCPU context and `FOLL_NOWAIT`. `KVM_PFN_ERR_RO_FAULT` intentionally returns `-EOPNOTSUPP`; higher layers must decide how to handle read-only mappings.

## Test Signals
Useful coverage includes guest page faults, async pfault enabled/disabled cases, memslot deletion races, MMU notifier invalidations during fault-in, read-only memslot writes, signal interruption, dirty writeback on release, gmap minor-fault fast path, and nested/vSIE shadow faults that pin multiple pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.h -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.h

## Purpose
Declares the s390 KVM fault-in helpers and provides inline utilities for simple GFN faulting, guest-page reads, releasing arrays of pinned guest faults, and checking invalidation retry needs across multiple faulted pages.

## Important APIs, Types, And Functions
Public declarations are `kvm_s390_faultin_gfn` and `kvm_s390_get_guest_page`. Inline helpers include `kvm_s390_faultin_gfn_simple`, `kvm_s390_get_guest_page_and_read_gpa`, `kvm_s390_release_multiple`, `kvm_s390_multiple_faults_need_retry`, `kvm_s390_get_guest_pages`, and array macros `kvm_s390_release_faultin_array`, `kvm_s390_array_needs_retry_unsafe`, and `kvm_s390_array_needs_retry_safe`.

## Control Flow
Simple callers build a `struct guest_fault` with GFN/write intent and delegate to `kvm_s390_faultin_gfn`. Shadow walkers can pin a page and immediately read an unsigned long from the host mapping via `kvm_s390_get_guest_page_and_read_gpa`. Multi-page users populate an array with `kvm_s390_get_guest_pages`, validate it against a saved invalidation sequence with the retry helpers, and release every valid page through `kvm_s390_release_multiple`.

## State And Persistence
The helpers only operate on caller-owned `struct guest_fault` objects. They set or clear `page`, `pfn`, `valid`, `write_attempt`, and related fields through the underlying implementation. No state is persisted beyond pinned page lifetime and any gmap changes performed by `kvm_s390_faultin_gfn`.

## Dependencies And Integration Points
Includes `linux/kvm_host.h` and `dat.h`. It wraps generic KVM page fault-in/release contracts and s390 MMU invalidation helpers. `gaccess.c` and `gmap.c` use the array helpers heavily while protecting vSIE shadow page tables.

## Risks And Edge Cases
The direct read helper dereferences `phys_to_virt(pfn_to_phys(f->pfn) | offset)` and assumes the pinned page remains valid until release. Multi-page retry helpers skip entries not marked valid, so callers must initialize arrays. Release helpers null out `page` but do not reset every other field. The `ignore` argument controls dirty/error accounting through `kvm_release_faultin_page`, so misuse can lose writeback or falsely dirty pages.

## Test Signals
Compile coverage plus nested-vSIE paths are the main signals. Tests should fault arrays of page-table pages, force MMU invalidation retries between pin and use, verify release on success and error paths, and run with debug page refcounting or leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gaccess.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gaccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gaccess.h -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/gaccess.h

## Purpose
Provides the public interface for s390 KVM guest memory access. It exposes address conversion helpers, lowcore accessors, logical/real/absolute read and write helpers, keyed access APIs, range-checking APIs, IPTE locking declarations, and vSIE shadow-fault entry points.

## Important APIs, Types, And Functions
Address helpers are `_kvm_s390_real_to_abs`, `kvm_s390_real_to_abs`, `_kvm_s390_logical_to_effective`, and `kvm_s390_logical_to_effective`. Lowcore helpers are `put_guest_lc`, `write_guest_lc`, and `read_guest_lc`. `enum gacc_mode` distinguishes fetch, store, and instruction fetch. Main APIs include `guest_translate_address_with_key`, `check_gva_range`, `check_gpa_range`, `access_guest_abs_with_key`, `access_guest_with_key`, `access_guest_real`, `cmpxchg_guest_abs_with_key`, `write_guest_with_key`, `read_guest_with_key`, `read_guest_instr`, `write_guest_abs`, `read_guest_abs`, `write_guest_real`, and `read_guest_real`. It also declares `ipte_lock`, `ipte_unlock`, `ipte_lock_held`, `kvm_s390_check_low_addr_prot_real`, `union mvpg_pei`, and `gaccess_shadow_fault`.

## Control Flow
Most inline wrappers select a mode and key, then delegate to the implementation in `gaccess.c`. Logical helpers use the vCPU PSW key unless a caller supplies an explicit access key. Instruction fetches force the translation mode needed by the architecture. Lowcore helpers apply the vCPU prefix and call raw KVM guest read/write helpers without key or low-address checks. Real helpers translate the real address through prefixing and then use the real-access implementation.

## State And Persistence
The header does not own state. It documents that many helpers may update `vcpu->arch.pgm` on positive program-interruption returns and that absolute/lowcore raw helpers may partially copy on host errors. The `union mvpg_pei` result carries shadow/MVPG partial-execution metadata such as DAT table address, not-PTE flag, DAT protection, and real-space indicator.

## Dependencies And Integration Points
Depends on KVM host types, uaccess, ptrace, and `kvm-s390.h`. It is included by diagnose, intercept, guest debug, gmap, and instruction-emulation code that needs architecture-correct guest memory access or exception reporting.

## Risks And Edge Cases
Callers must distinguish positive guest program-interruption codes from negative host errors. Raw absolute and lowcore helpers deliberately bypass storage-key and low-address protection and can partially copy. Logical access can allocate temporary GPA arrays and can require the IPTE lock. `put_guest_lc` assumes the destination is in lowcore; using it elsewhere is undefined by the local contract.

## Test Signals
Compile all s390 KVM users and run guest-memory access tests. Important cases are lowcore prefixing, DAT-off real access, logical address truncation, explicit versus PSW access keys, positive exception returns followed by `kvm_s390_inject_prog_cond`, and MVPG/vSIE callers consuming `union mvpg_pei`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gmap.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gmap.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/gmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/guestdbg.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/guestdbg.c

## Purpose
Implements s390 KVM guest debugging support using PER controls. It imports userspace hardware breakpoint/watchpoint requests, patches guest PER registers for single-step and hardware debug, filters guest PER events, detects watchpoint changes, and prepares `KVM_EXIT_DEBUG` exits.

## Important APIs, Types, And Functions
Public functions are `kvm_s390_backup_guest_per_regs`, `kvm_s390_restore_guest_per_regs`, `kvm_s390_patch_guest_per_regs`, `kvm_s390_import_bp_data`, `kvm_s390_clear_bp_data`, `kvm_s390_prepare_debug_exit`, `kvm_s390_handle_per_ifetch_icpt`, and `kvm_s390_handle_per_event`. Internal helpers include `extend_address_range`, `enable_all_hw_bp`, `enable_all_hw_wp`, `__import_wp_info`, `find_hw_bp`, `any_wp_changed`, `debug_exit_required`, `per_fetched_addr`, and `filter_guest_per_event`.

## Control Flow
When guest debug is enabled, KVM saves guest CR0/CR9/CR10/CR11, patches PER event/range controls for single-step or requested breakpoints/watchpoints, then restores the guest registers after the debug run window. Userspace breakpoint data is copied from user memory, split into breakpoint and write-watchpoint arrays, and watchpoints keep a backup copy of the original guest physical bytes. PER intercept handling first decides whether a userspace debug exit is required, then filters the remaining PER code so guest-requested PER events are still delivered accurately. Instruction-fetch PER handling rewinds PSW or decodes EXECUTE/EXECUTE RELATIVE LONG to find the actual fetched instruction address.

## State And Persistence
State is per-vCPU runtime debug state: saved control registers, breakpoint/watchpoint arrays, watchpoint `old_data` buffers, last breakpoint address, pending debug-exit flag, and `run->debug.arch` exit metadata. No durable persistence is used.

## Dependencies And Integration Points
Depends on KVM guest debug UAPI, s390 PER control bits, guest memory read helpers from `gaccess.h`, PSW rewind and instruction-length helpers, SIE intercept fields, and the intercept loop in `intercept.c`. It shares PER event filtering with normal guest PER delivery so host debug does not swallow guest-visible events accidentally.

## Risks And Edge Cases
PER ranges may wrap around address zero; `extend_address_range` and `in_addr_range` must handle overflow intervals. Breakpoints widen by up to six bytes to catch the preceding instruction fetch. Watchpoint detection compares memory after the event and can miss failures if reading guest memory fails or allocation for the temporary buffer fails. EXECUTE decoding must compute the executed target correctly. Single-step plus concurrent interrupts is intentionally deferred by intercept logic.

## Test Signals
Use s390 KVM guest-debug tests for single-step, hardware breakpoints, write watchpoints, wrapped address ranges, duplicate PER events, EXECUTE and EXECUTE RELATIVE LONG targets, guest PER passthrough, pending debug exits, and cleanup/reimport cycles with leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/guestdbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/intercept.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/intercept.c

## Purpose
Dispatches s390 SIE intercepts to in-kernel handlers or userspace fallback. It handles intercepted instructions, program/external interruptions, stop/validity/wait events, partial execution, selected protected-virtualization notifications, STHYI emulation, and post-instruction PER instruction-fetch processing.

## Important APIs, Types, And Functions
Exported functions are `kvm_s390_get_ilen`, `handle_sthyi`, and `kvm_handle_sie_intercept`. Internal handlers include `handle_stop`, `handle_validity`, `handle_instruction`, `inject_prog_on_prog_intercept`, `handle_itdb`, `should_handle_per_event`, `handle_prog`, `handle_external_interrupt`, `handle_mvpg_pei`, `handle_partial_execution`, `handle_operexc`, `handle_pv_spx`, `handle_pv_sclp`, `handle_pv_uvc`, `handle_pv_notification`, and `should_handle_per_ifetch`.

## Control Flow
`kvm_handle_sie_intercept` rejects ucontrol VMs for in-kernel handling, switches on `icptcode`, updates statistics, and delegates to instruction, program, external interrupt, wait, validity, stop, operation exception, partial execution, key-storage, interrupt-enable, and protected-virtualization handlers. Instruction intercepts dispatch by opcode group to the relevant s390 KVM emulation file, including diagnose handling. Program intercepts optionally process guest-debug PER events, guard against protected-guest specification loops, restore transactional-execution TDB data, and inject a program IRQ with detailed SIE-provided fields. External interrupt intercepts reinject priority-sensitive timer/external-call events or drop to userspace for interrupt loops. Partial MVPG execution faults in source and destination pages then retries the instruction.

Protected-virtualization notifications handle prefix changes, SCLP service interrupt completion, UVC remove-shared-access cleanup, and SIGP fallback. After many instruction-like intercepts, `should_handle_per_ifetch` may invoke `kvm_s390_handle_per_ifetch_icpt` so PER fetch events are delivered even when the instruction is handled by userspace.

## State And Persistence
State changes include vCPU stats, local interrupt state, vCPU stopped state, run exit reasons, reset/debug side effects via delegated handlers, lowcore TDB writes, injected IRQ queues, GPR condition-code/results for STHYI, prefix state for PV SPX, PV secure-page conversion, and SIE block interruption fields. All state is runtime VM/vCPU state.

## Dependencies And Integration Points
Integrates with all s390 KVM instruction handlers, `diag.c`, `gaccess.h` guest memory access, `faultin.h` page fault-in, guest debug PER handling, lowcore access, local/float interrupt injection, protected virtualization UV helpers, STHYI system information, SIGP, wait/stop handling, and KVM userspace exit conventions.

## Risks And Edge Cases
Return codes control whether KVM retries, injects, or exits to userspace; mixing guest exception codes with negative host errors is dangerous. Program-interruption injection must copy SIE fields such as TEID, access IDs, monitor codes, DXC, and PER data exactly. Specification and operation-exception loop avoidance protects host progress. MVPG PEI deliberately faults pages without key checking before retrying. PV notification handlers rely on SIDA data and UV retry semantics. PER fetch processing must be skipped when interrupts or key-storage retries would make an exit misleading.

## Test Signals
Run s390 KVM intercept selftests and guest workloads covering each intercept code, diagnose dispatch, program interruption injection fields, PER filtering/debug exits, stop/store-status, external timer/external-call priority, MVPG partial execution, STHYI, operation-exception userspace fallback, protected-virtualization prefix/SCLP/UVC notifications, and userspace fallback for unsupported intercepts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/intercept.c -->
