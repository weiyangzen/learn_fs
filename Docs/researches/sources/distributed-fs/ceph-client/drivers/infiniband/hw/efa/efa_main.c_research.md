# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_main.c

Owns EFA PCI probe/remove/shutdown, BAR and MSI-X setup, admin and AENQ initialization, event queue creation, and RDMA core registration.

Important functions include `efa_probe_device`, `efa_device_init`, `efa_enable_msix`, `efa_set_mgmnt_irq`, `efa_ib_device_add`, `efa_ib_device_remove`, `efa_create_eqs`, `efa_destroy_eqs`, management/completion IRQ handlers, and the PCI entry points `efa_probe`, `efa_remove`, and `efa_shutdown`. `efa_dev_ops` wires `efa_verbs.c` into RDMA core.

Probe enables PCI memory, allocates `struct efa_dev`, requests base BARs, maps the register BAR, initializes MMIO register reads, resets and validates firmware, sets DMA mask, enables MSI-X, requests the management IRQ, and initializes admin queues. RDMA registration fetches device attributes, requests the doorbell BAR, applies hardware hints, enables AENQ groups, creates completion EQs, sends host info, and registers the IB device.

Persistent state includes BAR addresses and mappings, doorbell BAR metadata, MSI-X vector indices, IRQ structs, EQ array, CQ xarray, device attributes, node GUID, and atomic stats. Dependencies include Linux PCI/IRQ/DMA/RDMA core, EFA admin/AENQ/EQ code, and verbs ops.

Risks are probe unwind ordering, IRQ races with CQ/EQ teardown, separate doorbell BAR ownership, shutdown ordering, and hardware hint unit conversion. Test signals include repeated load/unload, `ibv_devinfo`, CQ notifications, AENQ keep-alive counters, deferred probe on reset timeout, and fault injection at setup labels.
