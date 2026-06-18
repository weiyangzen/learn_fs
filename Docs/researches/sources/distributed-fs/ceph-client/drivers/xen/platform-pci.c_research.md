# sources/distributed-fs/ceph-client/drivers/xen/platform-pci.c

Purpose: binds the Xen platform PCI device used by HVM guests for event-channel callback delivery and grant-table frame setup when vector callbacks are unavailable or auto-translated grant frames are supplied through PCI MMIO.

Important APIs/functions: implements `platform_pci_probe`, `platform_pci_resume`, `do_hvm_evtchn_intr`, `xen_allocate_irq`, `get_callback_via`, and `alloc_xen_mmio`. Registers a built-in PCI driver for Xen platform device IDs.

Control flow: probe enables the PCI device, requests MMIO and I/O regions, records the MMIO aperture, and when vector callbacks are unavailable requests the platform IRQ, pins it to CPU0, computes ISA or PCI INTx callback encoding, and calls `xen_set_callback_via`. It allocates grant-frame MMIO space based on `gnttab_max_grant_frames`, initializes auto-xlat grant frames, then calls `gnttab_init`. Resume reprograms callback delivery if vector callbacks are not used.

State and persistence: global `platform_mmio`, `platform_mmio_alloc`, `platform_mmiolen`, and `callback_via` persist after probe. Grant-table auto-xlat mappings persist until failure cleanup or guest lifetime.

Dependencies and integration: depends on PCI resource management, Xen HVM callback parameters, event upcall handling through `xen_evtchn_do_upcall`, grant-table setup, xenbus headers, and Xen platform PCI IDs.

Risks: MMIO allocator is simple and BUGs on aperture overflow; IRQ callback delivery must reach CPU0 event ports; resource or grant-table init failures unwind IRQ and PCI regions; resume must restore callback method after device power transitions.

Test signals: boot HVM guests with and without vector callbacks, verify platform IRQ event delivery, suspend/resume callback restoration, grant-table initialization via platform MMIO, resource failure unwinds, and legacy Xen platform IDs.
