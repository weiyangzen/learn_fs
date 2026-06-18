# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_main.c

Owns ERDMA module init/exit, PCI probe/remove, BAR/IRQ/DMA-pool setup, command/event queue bring-up, capability discovery, RDMA registration, netdev association, resource allocator setup, and protocol-specific ops selection.

Important functions include `erdma_probe_dev`, `erdma_remove_dev`, `erdma_device_init`, `erdma_request_vectors`, `erdma_comm_irq_init`, `erdma_wait_hw_init_done`, `erdma_hw_reset`, `erdma_dev_attrs_init`, `erdma_device_config`, `erdma_res_cb_init`, `erdma_ib_device_add`, `erdma_device_register`, `erdma_netdev_event`, `erdma_init_module`, and `erdma_exit_module`.

Probe enables PCI, allocates `struct erdma_dev`, requests BARs, maps the function BAR, rejects zero-version functions, creates response/DB DMA pools, sets 64-bit DMA, allocates MSI-X, requests common IRQ, initializes AEQ/CMDQ, waits for hardware init, initializes CEQs, and arms CMDQ. RDMA registration queries caps/firmware via CMDQ, configures extended doorbells if supported, selects iWARP or RoCEv2 ops, initializes xarrays/resources/workqueue, reads peer MAC, binds to matching netdev, registers IB device, and registers a netdev notifier.

Persistent state includes BAR mapping, DMA pools, MSI-X vector count, common IRQ, AEQ/CMDQ/CEQs, attributes, resource bitmaps, QP/CQ xarrays, CEP list, context count, peer netdev, MTU, and reflush workqueue. Dependencies include PCI/MSI-X/DMA pools, RDMA core, netdevice notifier, ERDMA CMDQ/EQ/CM/QP/CQ/verbs.

Risks include long probe unwind ordering, IRQs observing freed queues, netdev association by permanent MAC and probe deferral, resource max initialization before bitmap allocation, and shared common IRQ coupling CMDQ and AEQ. Test signals include netdev-deferred probe, load/unload, MTU propagation, iWARP/RoCEv2 ops, capability decode, extended DB config, partial probe failure unwind, and PCI remove with open objects.
