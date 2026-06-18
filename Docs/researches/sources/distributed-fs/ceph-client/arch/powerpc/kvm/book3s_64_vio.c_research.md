# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_vio.c

## Purpose
Implements SPAPR virtual I/O TCE table support for 64-bit Book3S KVM. It creates mmap-able emulated TCE tables, attaches host IOMMU tables, translates guest TCEs to userspace and hardware mappings, and implements PAPR TCE hypercalls.

## Important APIs, Types, And Functions
Important APIs are `kvm_spapr_tce_release_iommu_group`, `kvm_spapr_tce_attach_iommu_group`, `kvm_vm_ioctl_create_spapr_tce`, `kvmppc_h_put_tce`, `kvmppc_h_put_tce_indirect`, `kvmppc_h_stuff_tce`, and `kvmppc_h_get_tce`. Helpers include `kvmppc_find_table`, `kvmppc_tce_pages`, `kvmppc_stt_pages`, `kvm_spapr_get_tce_page`, `kvmppc_tce_to_ua`, `kvmppc_tce_validate`, `kvmppc_tce_put`, `kvmppc_clear_tce`, `kvmppc_tce_iommu_map`, and `kvmppc_tce_iommu_unmap`.

## Control Flow
Table creation validates size/page shift/offset, charges locked memory, allocates a flexible table structure, rejects duplicate LIOBNs, creates an anonymous fd, and links the table into `kvm->arch.spapr_tce_tables`. Table pages are allocated lazily on mmap faults or nonzero TCE stores. IOMMU attach validates that a hardware table covers the guest DMA window, refs it, and records it with RCU/kref lifetime. `H_PUT_TCE` validates one TCE, maps or unmaps every attached IOMMU table, updates the emulated table, and rolls back hardware entries on failure. Indirect put validates up to 512 big-endian TCEs from guest memory, then maps each. Stuff TCE unmaps ranges and writes poison/zero values. Get TCE returns zero for unallocated pages or the stored entry in GPR4.

## State And Persistence
Per-VM state is the RCU list of SPAPR TCE tables. Each table stores LIOBN, page shift, offset, size, lazily allocated TCE pages, attached IOMMU tables, krefs, and a KVM reference held by the fd. Hardware IOMMU table mappings and userspace-entry arrays are mutated and persist until unmapped or released.

## Dependencies And Integration Points
Depends on KVM Book3S PAPR hypercall handling, Linux IOMMU table APIs, mm IOMMU pin/accounting helpers, KVM memslots/SRCU, anon inode fds, mmap fault handling, RCU, krefs, and PAPR TCE ABI constants. It integrates emulated devices, VFIO/IOMMU-backed passthrough, and userspace migration/inspection through the TCE fd.

## Risks And Edge Cases
Reference, RCU, and locked-memory accounting must be balanced across fd release, IOMMU group release, and attach races. Indirect TCE validation intentionally rereads userspace entries, relying on later checks to keep host safety. Attached IOMMU page shifts may be smaller than guest TCE page shifts, requiring subpage loops and full `iommu_tce_kill` coverage. The source snapshot includes duplicate local declarations and a duplicated function-call line in mapping code, which are compile risks if active. Lazy TCE pages mean zero entries are implicit.

## Test Signals
Use PAPR guests with virtio/vhost/VFIO DMA, create/destroy TCE windows, mmap TCE fds, attach/detach IOMMU groups, run `H_PUT_TCE`, `H_PUT_TCE_INDIRECT`, `H_STUFF_TCE`, and `H_GET_TCE`, test invalid LIOBN/IOBA/page shift/offsets, stress table fd release during DMA window changes, and verify locked memory accounting returns to zero.
