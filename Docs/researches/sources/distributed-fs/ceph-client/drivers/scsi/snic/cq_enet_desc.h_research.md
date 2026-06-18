# sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_enet_desc.h

Purpose: this header defines the Ethernet work-queue completion descriptor format used by SNIC to acknowledge posted host request descriptors.

Important APIs, types, and functions: `struct cq_enet_wq_desc` mirrors the common 16-byte CQ descriptor with reserved type-specific bytes. `cq_enet_wq_desc_dec()` delegates to `cq_desc_dec()` to extract type, color, queue number, and completed index.

Control flow: SNIC's WQ completion path services CQ entries for posted host requests, decodes this descriptor, and then calls `svnic_wq_service()` to free or mark WQ buffers whose indexes have completed.

State and persistence: no state is held here. Descriptor state lives in the DMA CQ ring and in each WQ buffer's `os_buf`, DMA address, and posted indexes.

Dependencies and integration: includes `cq_desc.h` and is used by `snic_io.c` and `snic_res.c` when allocating and servicing the WQ-associated completion queue.

Risks: the file intentionally treats the descriptor as the generic `cq_desc`; any type-specific data added by hardware would be ignored. Correct memory ordering relies on `cq_desc_dec()`.

Test signals: WQ completion interrupt tests should verify that request DMA mappings are eventually unmapped or acknowledged and that ring indices are advanced correctly when the CQ wraps.
