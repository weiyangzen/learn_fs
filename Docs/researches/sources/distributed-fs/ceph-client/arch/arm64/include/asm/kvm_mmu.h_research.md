# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mmu.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mmu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mmu.h

### Purpose
`kvm_mmu.h` declares ARM64 KVM MMU and hyp mapping helpers, plus inline address-translation, cache-maintenance, VTTBR, stage-2 loading, and fault-lock policies.

### Important APIs, Types, And Functions
Key exports are hyp assembly macros `hyp_pa` and `hyp_kimg_va`, `__kern_hyp_va()`, `kern_hyp_va()`, `KVM_PHYS_SHIFT`, `kvm_phys_shift()`, hyp mapping APIs (`create_hyp_mappings`, `hyp_alloc_private_va_range`, `create_hyp_io_mappings`, `create_hyp_stack`), stage-2 APIs (`kvm_stage2_unmap_range`, `kvm_init_stage2_mmu`, `kvm_handle_guest_abort`), cache helpers, `kvm_get_vttbr()`, `__load_stage2()`, `kvm_fault_lock()`, and cacheable PFNMAP support checks.

### Control Flow
Early KVM setup computes hyp VA layout and creates hyp mappings. Guest fault paths take the appropriate MMU lock, map/unmap/update stage-2 entries, perform cache maintenance when FWB/DIC do not cover it, and load VTCR/VTTBR before guest entry.

### State, Persistence, And Dependencies
State includes hyp VA layout, hyp phys/virt offset, stage-2 page tables, VMIDs, and cache/TLB side effects. It depends on page-table allocation, cacheflush, MMU context, `kvm_pgtable.h`, `stage2_pgtable.h`, and KVM vCPU emulation.

### Integration Points
Connects KVM guest memory management with generic MM, hyp mapping setup, TLB maintenance, pKVM isolation, and abort handling.

### Risks
Incorrect hyp VA conversion breaks nVHE execution. Missing cache maintenance can expose stale instructions/data to guests. VTTBR ordering relies on prior barriers, and fault locking differs in protected mode.

### Test Signals
Run KVM memory faults, dirty logging, MMIO/ioremap, huge-page split, protected-mode tests, VMID rollover, cache aliasing workloads, and guest instruction-cache coherency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mmu.h -->
