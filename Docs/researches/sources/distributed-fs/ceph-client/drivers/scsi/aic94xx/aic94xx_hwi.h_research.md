# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.h

Purpose: central hardware-interface data model for the AIC94xx driver, defining host adapter state, hardware profile, DMA tokens, active SCBs, sequencer queues, ports, and inline allocation/index helpers.

Important APIs/types/functions: defines `ASD_MAX_PHYS`, `struct asd_ha_addrspace`, `bios_struct`, `unit_element_struct`, `flash_struct`, `asd_phy_desc`, `asd_dma_tok`, `hw_profile`, `asd_ascb`, `asd_seq_data`, `asd_port`, and `asd_ha_struct`. Inline helpers allocate/free coherent DMA tokens, initialize ASCBS, manage `tc_index` bitmaps, and free single/list ASCBS. Prototypes expose hardware init, ISR, SCB posting, ESCB posting, PHY control, LED control, timeout, and reset functions.

Control flow: inline allocation helpers wrap slab and DMA APIs. `asd_tc_index_get/release/find()` are lock-required index-map operations used when posting and completing SCBs. `asd_ascb_free()` asserts list removal, releases the index, frees the DMA SCB, and returns the ASCB to cache.

State and persistence: `asd_ha_struct` owns PCI device binding, libsas HA, IO windows, hardware profile, PHY/port arrays, SCB DMA pool, sequencer state, BIOS status, and loaded firmware pointer. This is per-adapter runtime state, freed on remove.

Dependencies and integration: includes interrupts, PCI, DMA mapping, libsas, top-level aic94xx declarations, and SAS hardware structure definitions. It is shared by init, hwi, reg, task, TMF, SDS, and dump code.

Risks and test signals: helpers assume required locks and valid indices; freeing an ASCB with `tc_index == -1` or while still linked trips bugs or corrupts bitmaps. Per-adapter cleanup must mirror all allocations. Build and runtime tests should cover probe/remove, SCB allocation exhaustion, completion after timeout, EDB/ESCB teardown, and multiple adapters.
