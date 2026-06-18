# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_hv.c

## Purpose
Implements Book3S HV hash-MMU management and hash/radix delegation for KVM-HV. It allocates and resets guest HPTs, maps VRMA, translates HV hash entries, handles hash page faults and MMIO emulation, manages reverse maps, aging and dirty logging, supports HPT resize and migration file descriptors, and exposes debugfs HPT dumps.

## Important APIs, Types, And Functions
Important APIs include `kvmppc_allocate_hpt`, `kvmppc_set_hpt`, `kvmppc_alloc_reset_hpt`, `kvmppc_free_hpt`, `kvmppc_map_vrma`, `kvmppc_mmu_hv_init`, `kvmppc_book3s_hv_page_fault`, `kvmppc_rmap_reset`, `kvm_unmap_gfn_range_hv`, `kvmppc_core_flush_memslot_hv`, `kvm_age_gfn_hv`, `kvm_test_age_gfn_hv`, `kvmppc_hv_get_dirty_log_hpt`, `kvmppc_pin_guest_page`, `kvmppc_unpin_guest_page`, `kvm_vm_ioctl_resize_hpt_prepare`, `kvm_vm_ioctl_resize_hpt_commit`, `kvm_vm_ioctl_get_htab_fd`, `kvmppc_mmu_debugfs_init`, and `kvmppc_mmu_book3s_hv_init`. Internal structures include `struct kvm_resize_hpt`, `struct kvm_htab_ctx`, and `struct debugfs_htab_state`.

## Control Flow
HPT allocation obtains CMA or normal pages, zeroes the table, allocates a reverse-map array, and stores SDR1. Reset blocks vCPUs via `mmu_setup_lock`/`mmu_ready`, switches radix VMs back to HPT if needed, clears or reallocates the table, resets rmaps, and requests TLB flushes. Hash page fault handling verifies the real-mode-found HPTE, translates GPA, handles MMIO for missing memslots, faults in host pages, checks host PTE attributes and WIMG compatibility, locks HPTE/rmap chains, installs the real HPTE, and records R/C bits. Rmap functions unmap, age, test age, and clear dirty bits by walking HPTE chains. Resize prepare allocates a new HPT asynchronously; commit stops vCPUs, rehashes bolted entries, pivots tables, and resumes the VM. HPT fd read/write serializes or restores guest HPTE state for migration.

## State And Persistence
Per-VM persistent runtime state includes `kvm->arch.hpt`, reverse maps in memslots, `mmio_update`, `mmu_ready`, resize work state, LPID, VRMA SLB value, and HPTE modification interest. Per-vCPU state includes page-fault cache fields, SLB entries, and MMU callback pointers. Migration read/write exposes HPT state through an anonymous inode; debugfs exposes a read-only textual view.

## Dependencies And Integration Points
Depends on PPC hash MMU operations, KVM-HV hcall implementation, rmap helpers, KVM SRCU and MMU notifier sequencing, Linux page faulting, memslot dirty bitmaps, debugfs, anon inode APIs, radix helpers for radix VMs, pseries/powernv LPID behavior, and partition table setup on POWER9+. It integrates with QEMU migration through `KVM_GET_HTAB_FD` and HPT resize ioctls.

## Risks And Edge Cases
This is one of the highest-risk files in the subset. HPTE lock ordering against rmap locks is explicit to avoid ABBA deadlocks. Dirty/reference bit harvesting is inherently racy with running vCPUs. HPT resize must stop vCPUs and preserve bolted entries without losing rmaps. MMIO emulation reads the faulting instruction after translation and must avoid advancing the PC on mismatched prefixed/non-prefixed instructions. The source snapshot has duplicated lines in control blocks, which are compile/logic risks if present. Attribute mismatches, huge-page alignment, secure/nested transitions, and hash-vs-radix dispatch all need careful coverage.

## Test Signals
Run KVM-HV hash guests through VRMA boot, H_ENTER/H_REMOVE, hash faults, MMIO loads/stores including prefixed instructions, dirty logging with huge pages, live migration via HPT fd, HPT resize prepare/commit/cancel, memory slot deletion, page aging, nested disabled/enabled builds, POWER7/8/9 variants, and debugfs HPT reads. Stress with concurrent vCPUs and host MMU invalidations.
