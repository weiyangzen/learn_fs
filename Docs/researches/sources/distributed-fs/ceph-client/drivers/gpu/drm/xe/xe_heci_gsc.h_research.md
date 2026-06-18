# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.h

Purpose: declares the Xe HECI/GSC auxiliary-device state, interrupt bit helpers, and public init/IRQ entry points.

Important APIs/types: `GSC_IRQ_INTF`, `CSC_IRQ_INTF`, `struct xe_heci_gsc`, `xe_heci_gsc_init`, `xe_heci_gsc_irq_handler`, and `xe_heci_csc_irq_handler`.

Control flow/state: `struct xe_heci_gsc` is embedded in `struct xe_device` and persists the MEI auxiliary device pointer and allocated IRQ number. The bit helpers encode GSC HECI1/2 and CSC HECI1/2 interrupt positions.

Dependencies/integration: forward-declares `struct xe_device` and `struct mei_aux_device`, bridging Xe device code to the MEI auxiliary bus.

Risks/test signals: bit helper changes affect IRQ routing. Tests should confirm GSC/CSC interrupt filters call the generic IRQ only for the intended interface bit and only when the feature is present.
