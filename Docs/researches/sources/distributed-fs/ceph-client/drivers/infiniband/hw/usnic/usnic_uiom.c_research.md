# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.c

Purpose: userspace I/O memory registration and IOMMU mapping for usNIC protection domains.

Important APIs/functions: `usnic_uiom_reg_get()`, `usnic_uiom_reg_release()`, `usnic_uiom_alloc_pd()`, `usnic_uiom_dealloc_pd()`, `usnic_uiom_attach_dev_to_pd()`, `usnic_uiom_detach_dev_from_pd()`, `usnic_uiom_get_dev_list()`, and `usnic_uiom_free_dev_list()`. Internal helpers pin pages, build SG chunks, compute interval diffs, map/unmap IOMMU ranges, and handle DMA faults.

Control flow: PD allocation creates an IOMMU paging domain with a fault handler. VF binding attaches a device to the domain and records it. MR registration pins long-term user pages under memlock accounting, builds chunks, computes intervals not already mapped in the PD interval tree, maps contiguous physical spans into IOVA equal to userspace VA page addresses, then inserts intervals. Release removes intervals, unmaps pages no longer referenced, unpins dirty writable pages, decrements pinned VM, and drops the owning mm reference.

State and persistence: `usnic_uiom_pd` owns an IOMMU domain, interval tree root, device list/count, and spinlock. `usnic_uiom_reg` owns VA/length/offset/writable state, chunk list, owning mm, and PD pointer. Pinned pages and IOMMU mappings persist until MR deregistration.

Dependencies and integration: depends on Linux GUP/pinning, IOMMU domain APIs, scatterlists, mm accounting, and the usNIC interval tree implementation. Called by PD/MR and QP group VF binding paths.

Risks: long-term page pinning and memlock accounting are delicate; error path subtracts remaining `npages` rather than total pinned count after partial progress. All mappings are forced writable due to Intel IOMMU permission-change behavior. IOVA equals userspace VA, so overlapping registrations rely on interval diff correctness. `usnic_uiom_detach_dev_from_pd()` returns a value from a void function in this source, which is syntactically suspicious in strict builds.

Test signals: MR registration/release with overlapping and non-overlapping ranges, writable/dirty behavior, memlock limit enforcement, IOMMU attach/detach failure paths, DMA fault logging, interval unmap correctness, and stress with VF sharing.
