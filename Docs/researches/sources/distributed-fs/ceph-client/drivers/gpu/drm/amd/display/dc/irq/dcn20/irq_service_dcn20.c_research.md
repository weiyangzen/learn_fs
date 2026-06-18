# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c

Purpose: implements the DCN 2.0 ASIC interrupt service factory. It maps hardware interrupt `src_id`/`ext_id` values into the stable `enum dc_irq_source` namespace and provides the MMIO register table used by the shared `dal_irq_service_set()` and `dal_irq_service_ack()` paths.

Important APIs and functions: `dal_irq_service_dcn20_create()` allocates an `irq_service`, `dcn20_irq_construct()` installs `irq_source_info_dcn20` and `irq_service_funcs_dcn20`, and `to_dal_irq_source_dcn20()` handles vblank, vline0, page-flip, vupdate-no-lock, HPD, and HPD RX source translation. The file defines table-entry macros for HPD, HPD RX, HUBP surface flip, OTG vupdate, OTG vstartup/vblank, OTG vertical interrupt 0, plus dummy I2C/DPSINK/GPIO/underflow entries.

Control flow: the interrupt dispatcher calls `dal_irq_service_to_irq_source()`, which reaches `to_dal_irq_source_dcn20()`. Consumers then enable or acknowledge the returned source through the shared service. HPD entries use `hpd0_ack()` to acknowledge and flip polarity based on delayed sense state; most other real entries rely on generic register writes because their callback structs have NULL `set`/`ack`.

State and persistence: the service is heap allocated with `kzalloc_obj()` and owns no dynamic state beyond `ctx`, `info`, and `funcs`. The IRQ table is static const and persists for the module lifetime. Hardware state is changed through enable and ack MMIO masks in HPD, HUBPREQ, and OTG registers.

Dependencies and integration points: includes DCN 2.0 offsets/masks, `irqsrcs_dcn_1_0.h`, `dm_services.h`, and DCE110 dummy/HPD helpers. It integrates with the display manager's interrupt registration path through the exported `dal_irq_service_dcn20_create()` symbol.

Risks: table indexes must match `enum dc_irq_source`; incorrect mask polarity or clear bits can leave interrupts stuck or disabled. DCN20 has six HPD/RX, six vblank/vline/vupdate, and six pflip mappings, so reduced-pipe ASICs should not reuse this table without auditing. HPD callback reuse assumes HPD0 field names are macro-compatible for all instances.

Test signals: compile coverage catches register macro drift; runtime evidence is successful hotplug, page flip, vblank, vline, and vupdate interrupt delivery on DCN20 hardware. Negative tests should verify unsupported I2C/DPSINK/GPIO/underflow dummy entries warn/assert if enabled or acked.
