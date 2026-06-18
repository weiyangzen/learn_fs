# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c

Purpose: DCN 2.0.1 interrupt service implementation for a smaller display configuration. It follows the DCN20 pattern but narrows active translations and table entries to the supported pipes/connectors.

Important APIs and functions: `to_dal_irq_source_dcn201()` maps two vblank, two vline0, two vupdate, two HPD, and two HPD RX interrupt IDs. The static `irq_source_info_dcn201` table contains HPD/RX entries for instances 0 and 1, pflip entries for 0 through 3, active vblank/vupdate/vline entries for 0 and 1, and dummy placeholders for unsupported sources. `dal_irq_service_dcn201_create()` allocates and constructs the service.

Control flow: hardware source IDs are translated before generic enable/ack operations consume the table. The generic IRQ write path is used for pflip, vblank, vline0, and vupdate-no-lock; HPD uses `hpd0_ack()`. The constructor binds the static table and `irq_service_funcs_dcn201`.

State and persistence: no mutable per-source software state is stored. The static table persists; hardware enable and ack state is persisted in HPD, HUBPREQ, and OTG registers until changed.

Dependencies and integration points: uses DMU/DCN 2.0.1 register base macros, DCN 1.0 interrupt source IDs, and the DCE110 dummy/HPD helper interface. It plugs into ASIC initialization through `dal_irq_service_dcn201_create()`.

Risks: the file maps pflip entries for four HUBP instances but only maps interrupt source IDs for two HUBP flip interrupts, which requires hardware-specific validation. Accidentally enabling dummy entries for HPD3+ or vblank3+ indicates a caller/hardware mismatch.

Test signals: validate hotplug and HPD RX on the first two connectors, vblank/vline/vupdate interrupt delivery for the first two OTGs, and page flip behavior on supported planes. Build failures indicate register offset or mask drift.
