# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_radix.c

## Purpose
Implements Book3S HV radix-MMU support: guest radix table walking, guest memory copy through LPID/PID contexts, second-level radix page-table creation and teardown, radix page fault handling, TLB/PWC invalidation, aging and dirty logging, RMMU capability reporting, secure guest handling, nested rmap integration, debugfs dumps, and radix page-table slab cache lifecycle.

## Important APIs, Types, And Functions
Key APIs are `__kvmhv_copy_tofrom_guest_radix`, `kvmhv_copy_from_guest_radix`, `kvmhv_copy_to_guest_radix`, `kvmppc_mmu_walk_radix_tree`, `kvmppc_mmu_radix_translate_table`, `kvmppc_mmu_radix_xlate`, `kvmppc_radix_tlbie_page`, `kvmppc_unmap_pte`, `kvmppc_free_pgtable_radix`, `kvmppc_free_radix`, `kvmppc_create_pte`, `kvmppc_hv_handle_set_rc`, `kvmppc_book3s_instantiate_page`, `kvmppc_book3s_radix_page_fault`, `kvm_unmap_radix`, `kvm_age_radix`, `kvm_test_age_radix`, `kvmppc_hv_get_dirty_log_radix`, `kvmppc_radix_flush_memslot`, `kvmhv_get_rmmu_info`, `kvmppc_init_vm_radix`, `kvmhv_radix_debugfs_init`, `kvmppc_radix_init`, and `kvmppc_radix_exit`.

## Control Flow
Guest copy uses pseries hypercalls when necessary or switches LPID/PID and copies through radix quadrants with page faults disabled. Translation walks process/partition table entries, validates supported radix geometry, reads guest PTEs, and derives GPA and permissions. Page faults reject unsupported DSISR cases, translate `fault_gpa`, hand secure pages to the ultravisor, emulate MMIO for missing memslots, reflect readonly writes as DSI, optionally handles hardware set-R/C failures, faults in host pages, chooses 4K/2M/1G mappings when dirty logging and alignment allow, and inserts second-level PTEs under `mmu_lock`. Unmap/free paths recursively clear page tables, flush TLB/PWC, update dirty maps, and remove nested rmaps.

## State And Persistence
Per-VM state includes `arch.pgtable`, process-table pointer, LPID, secure guest flags, large-page counters, nested rmaps, and MMU invalidation sequence. Slab caches `kvm_pte_cache` and `kvm_pmd_cache` persist while KVM radix support is loaded. Guest page-table R/C state and KVM dirty bitmaps are updated as part of fault and dirty-log handling.

## Dependencies And Integration Points
Depends on radix MMU helpers, pseries `H_COPY_TOFROM_GUEST`, RPT invalidate hypercalls, ultravisor/secure guest APIs, KVM memslots and MMU notifiers, nested-HV rmap helpers, Linux page-table allocation, debugfs, and Power9-supported radix geometry. It is dispatched from the HV MMU path when `kvm_is_radix(kvm)` is true.

## Risks And Edge Cases
LPID/PID switching must restore host state exactly and is disabled for nestedv2. Geometry validation rejects unsupported guest trees but must return the right guest-visible fault. Large-page insertion races with existing smaller mappings and invalidations; `PTE_BITS_MUST_MATCH` limits acceptable concurrent differences. Dirty logging forces 4K mappings. Secure guest state bypasses normal unmap/age/dirty behavior. The source snapshot contains duplicate declarations in `kvm_radix_test_clear_dirty`, a compile risk if active. TLB invalidation differs between bare metal, pseries hcalls, and RPT invalidate firmware.

## Test Signals
Boot radix HV guests with 4K and 64K base pages, exercise 4K/2M/1G mappings, dirty logging transitions, memslot removal, MMIO faults, DSISR set-R/C handling, secure guest page sharing, nested guest shadow pgtable updates, RMMU info ioctl, debugfs radix output, pseries and powernv invalidation paths, and slab init/exit failure paths.
