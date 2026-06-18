<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/gdma.h -->
# sources/distributed-fs/ceph-client/include/net/mana/gdma.h

## Purpose
`gdma.h` is the core Microsoft Azure MANA GDMA hardware ABI and driver-internal interface. It defines request/response messages, queue formats, doorbells, DMA-region and memory-registration commands, capability negotiation, context state, and exported GDMA helper functions.

## Important APIs, types, and functions
Key types include `struct gdma_context`, `struct gdma_dev`, `struct gdma_queue`, `struct gdma_queue_spec`, `struct gdma_mem_info`, `struct gdma_resource`, `union gdma_doorbell_entry`, `struct gdma_req_hdr`, `struct gdma_resp_hdr`, queue WQE/CQE/EQE formats, and many HW command structs. Main functions are `mana_gd_init_req_hdr`, queue create/destroy/poll/ring helpers, work-request posting, resource-map allocation, DMA memory allocation/free, HWC request sending, debugfs registration, RDMA service events, suspend/resume, and logging policy.

## Control flow
The driver negotiates GDMA protocol/capability flags, lists and registers devices, creates DMA regions and queues, posts WQEs into SQ/RQ queues, rings doorbells, polls CQ/EQ owner-bit entries, and uses HWC commands for resource management. Queue head/tail semantics differ by queue type: SQ/RQ producer/consumer indexes are in 32-byte basic units, while EQ/CQ consume entries using owner bits.

## State and persistence
Persistent hardware-visible state includes queue IDs, doorbell IDs, PD IDs, GPA memory keys, DMA region handles, registered devices, MSI-X vectors, BAR mappings, and capability flags. Kernel runtime state includes xarray IRQ contexts, CQ tables, queue memory metadata, service workqueues, probe/service flags, and debugfs dentries. Hardware state survives until explicit destroy/deregister or PCI reset.

## Dependencies and integration points
It depends on PCI/device APIs, DMA mapping, netdevice types, auxiliary devices, xarray, debugfs, workqueues, completions, shared-memory bootstrap (`shm_channel.h`), and HWC (`hw_channel.h`). It is the common substrate for MANA Ethernet and MANA RDMA devices.

## Risks and test signals
Risks include bitfield ABI drift, natural-alignment assumptions for HW DATA structs, queue owner-bit wrap bugs, doorbell tail-unit mistakes, DMA page alignment and large-page capability negotiation, resource bitmap locking, HWC timeout/recovery handling, dynamic MSI-X allocation, and leaked hardware handles on partial failure. Tests should cover VF version negotiation, queue create/destroy, WQE post/ring, CQ/EQ wrap, DMA-region add-pages paths, suspend/resume, service EQEs, and capability-flag compatibility.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/gdma.h` completely for this pass (1021 lines, 22785 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/gdma.h -->
