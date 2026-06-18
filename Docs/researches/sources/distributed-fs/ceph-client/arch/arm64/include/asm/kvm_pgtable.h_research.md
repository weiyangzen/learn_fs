# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pgtable.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pgtable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pgtable.h

### Purpose
`kvm_pgtable.h` defines the generic ARM64 KVM page-table library interface for hyp stage-1 and guest stage-2 tables, including PTE encoding, walkers, mapping/unmapping, permission changes, aging, flushing, splitting, and pKVM annotations.

### Important APIs, Types, And Functions
It defines `kvm_pte_t`, PTE address/attribute masks, invalid PTE annotation types, `kvm_pte_to_phys()`, `kvm_phys_to_pte()`, granule/block helpers, `struct kvm_pgtable_mm_ops`, `enum kvm_pgtable_prot`, `enum kvm_pgtable_walk_flags`, `struct kvm_pgtable_visit_ctx`, `struct kvm_pgtable_walker`, `struct kvm_pgtable`, and APIs such as `kvm_pgtable_hyp_init/map/unmap/destroy`, `kvm_get_vtcr()`, `kvm_pgtable_stage2_*`, `kvm_pgtable_walk()`, `kvm_pgtable_get_leaf()`, and `kvm_tlb_flush_vmid_range()`.

### Control Flow
Callers initialize a page-table object with memory callbacks, then use map/unmap/walk APIs. Walkers visit leaf and table entries in requested order, using RCU for shared host walks but forbidding shared walks in hyp context. Stage-2 operations coalesce/split mappings, relax permissions, age entries, and issue required TLB/cache maintenance.

### State, Persistence, And Dependencies
State is page-table memory, reference counts in callback-owned pages, stage-2 MMU metadata, and optional pKVM mapping trees. It depends on generic KVM host types, ARM64 page-table hardware definitions, RCU in host context, and CPU LPA2/52-bit PA capabilities.

### Integration Points
Consumed by KVM MMU, pKVM host/guest ownership tracking, nested translation, dirty logging, huge-page splitting, and hyp mapping code.

### Risks
Break-before-make, shared-walker synchronization, LPA2 address encoding, and invalid PTE annotations are high-risk. Caller-provided `mm_ops` must obey refcount/free semantics.

### Test Signals
KVM page-table unit tests, stage-2 map/unmap/relax-perms/young tests, huge-page split tests, pKVM donation/reclaim tests, LPA2/52-bit PA builds, and RCU lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pgtable.h -->
