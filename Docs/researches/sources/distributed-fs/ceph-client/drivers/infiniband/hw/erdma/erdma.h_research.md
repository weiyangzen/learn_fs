# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma.h

Defines core ERDMA driver state, queue structs, device attributes, resource allocators, register accessors, and cross-file prototypes.

Important types include `erdma_eq`, `erdma_cmdq_sq`, `erdma_cmdq_cq`, `erdma_comp_wait`, `erdma_cmdq`, `erdma_devattr`, `erdma_irq`, `erdma_eq_cb`, `erdma_resource_cb`, and the root `struct erdma_dev`. Helpers include `get_queue_entry`, `to_edev`, register read/write wrappers, and `ERDMA_GET`.

The header has no standalone runtime flow, but it defines the shared call graph between probe, command queue, event queues, verbs, CQ, QP, and CM. `struct erdma_dev` persists the IB device, netdev, PCI function, BAR mapping, attributes, command/async/completion queues, resource bitmaps, QP/CQ xarrays, context count, CEP list, DMA pools, workqueue, and protocol type.

Dependencies include Linux bitfield, netdevice, PCI, xarray, RDMA core, and `erdma_hw.h`. Risks include ownership mistakes across files, queue index wrap bugs, and register helpers used before BAR mapping. Test signals include clean compile, probe/remove leak tests, xarray lookup under interrupts, command waits, and resource bitmap exhaustion/reuse.
