# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.c

Purpose: this file implements the generic vNIC device layer used by SNIC: resource discovery from BAR0, coherent descriptor ring allocation, devcmd2 command submission, firmware info/config/stat/notify/open/init/enable/disable commands, notify checksum handling, and vNIC registration cleanup.

Important APIs, types, and functions: internal `struct vnic_dev` tracks PCI device, resources, interrupt mode, devcmd2 controller, notify/stats/fw_info DMA buffers, and command args. `vnic_dev_discover_res()` parses the BAR resource table. `svnic_dev_alloc_desc_ring()` and `svnic_dev_free_desc_ring()` manage aligned coherent rings. `svnic_dev_init_devcmd2()` allocates a devcmd2 WQ and result ring and issues `CMD_INITIALIZE_DEVCMD2`. `svnic_dev_cmd()` wraps command execution. Public helpers implement `svnic_dev_spec()`, stats dump/clear, notify set/unset, link status/down count, open/open_done, init, enable/disable, close, and unregister.

Control flow: probe calls `svnic_dev_alloc_discover()`, `svnic_dev_cmd_init()`, then vNIC open/init/config flows. Devcmd2 posts a command descriptor to a WQ, rings `posted_index`, waits for the corresponding result color, copies result args for read commands, and handles error/timeout. Notify reads copy a DMA buffer until its checksum is stable.

State and persistence: all state is runtime. Coherent DMA buffers cache firmware info, stats, notify area, devcmd2 command/result rings, and normal descriptor rings. `vdev->intr_mode` is software state used by SNIC setup.

Dependencies and integration: depends on vNIC resource definitions, devcmd ABI, vNIC WQ helpers, PCI DMA, MMIO I/O accessors, and SNIC probe/resource code.

Risks: devcmd2 result color management is critical. The code checks `0xFFFFFFFF` fetch/posted indexes as hardware removal indicators. Resource discovery bounds checking handles strided resources but uses BAR0 length for all BAR offsets in this single-BAR driver. `svnic_dev_cmd()` assumes `devcmd_rtn` is initialized. Notify checksum loop can spin until a consistent copy is seen.

Test signals: resource table validation, missing devcmd2 resource, devcmd timeout/error, hardware surprise removal, notify checksum stability, stats/firmware info DMA allocation failure, open/init/enable/disable sequencing, and unregister after partial initialization.
