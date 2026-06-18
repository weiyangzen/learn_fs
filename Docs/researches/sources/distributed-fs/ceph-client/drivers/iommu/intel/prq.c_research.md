<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/prq.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/prq.c

Purpose: Intel VT-d Page Request Queue support for PRI/IOPF. It allocates and programs PRQ rings, handles page-request interrupts, validates and reports PRQ descriptors to the generic IOPF layer, drains PRQ state during PASID teardown, and sends page-group responses.

Important APIs/types/functions: `struct page_req_dsc` models hardware descriptors. Public functions are `intel_iommu_enable_prq()`, `intel_iommu_finish_prq()`, `intel_iommu_drain_pasid_prq()`, and `intel_iommu_page_response()`. Core helpers include `prq_event_thread()`, `intel_prq_report()`, `handle_bad_prq_event()`, and `prq_to_iommu_prot()`.

Control flow: enabling allocates a PRQ page ring, DMAR IRQ vector, generic `iopf_queue`, threaded IRQ, initializes head/tail/PQA registers, and completion. The IRQ thread clears pending status, walks descriptors from head to tail, rejects non-canonical/unsupported request combinations, drops stop markers, finds the requesting device by RID under `iopf_lock`, reports valid faults to `iommu_report_device_fault()`, traces descriptors, advances PQH, handles overflow by discarding partial IOPF groups when drained, and completes waiters. Draining waits for matching descriptors to leave software and hardware queues, flushes the generic IOPF workqueue, then submits wait/IOTLB/devTLB descriptors with drain semantics until hardware reports no PRQ overflow.

State and persistence: `iommu->prq`, `pr_irq`, `iopf_queue`, names, sequence counter, `prq_complete`, and hardware PRQ registers persist while PRQ is enabled. Device `iopf_refcount` determines whether drain is needed.

Dependencies and integration: integrates Intel queued invalidation, device RID lookup, generic `io-pgfault.c`, PCI ATS/PRI, PASID teardown, tracepoints, and DMAR hwirq allocation.

Risks: PRQ drain assumes the device driver has stopped DMA and no new requests arrive. Bad descriptor response uses RID as DID in response fields per hardware format. Overflow recovery can discard partial groups. Device lookup and IOPF queue removal must be synchronized to avoid reporting to freed domains.

Test signals: PRI-capable device SVA faults, invalid descriptor injection, stop-marker handling, overflow and partial discard, PASID teardown drain, page response success/failure, IRQ allocation unwind, and tracepoint decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/prq.c -->
