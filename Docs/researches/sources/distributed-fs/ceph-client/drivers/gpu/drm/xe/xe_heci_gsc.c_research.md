# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.c

Purpose: creates the auxiliary MEI/HECI device used to communicate with the Graphics Security Controller firmware and forwards GSC/CSC HECI interrupts from Xe IRQ handling to that auxiliary device.

Important functions/types: `struct heci_gsc_def`, platform definitions for DG1/DG2/PVC/Battlemage, `heci_gsc_irq_init`, `heci_gsc_irq_setup`, `heci_gsc_add_device`, `xe_heci_gsc_init`, `xe_heci_gsc_irq_handler`, `xe_heci_csc_irq_handler`, and cleanup `xe_heci_gsc_fini`.

Control flow: init checks `has_heci_gscfi`/`has_heci_cscfi`, selects a platform BAR definition, registers managed cleanup, optionally allocates a Linux IRQ descriptor unless polling/survivability boot mode is active, constructs a `mei_aux_device` with BAR resource under PCI BAR0, initializes it as an auxiliary device, and adds it. IRQ handlers filter IIR bits, check feature support and valid IRQ, then call `generic_handle_irq_safe`.

State/persistence: `xe->heci_gsc` stores the auxiliary device pointer and IRQ number. Cleanup deletes/uninitializes the auxiliary device and frees the IRQ descriptor.

Dependencies/integration: integrates Linux auxiliary bus, MEI aux driver, PCI resources, GSC register base definitions, DRM logging, and survivability mode.

Risks/test signals: wrong BAR offsets or IRQ bit mapping break GSC firmware communication. Cleanup must not leak `mei_aux_device` or IRQ descriptors on partial failure. Test unsupported platforms, polling/survivability boot, aux init/add failures, GSC versus CSC IRQ feature mismatches, and repeated init cleanup.
