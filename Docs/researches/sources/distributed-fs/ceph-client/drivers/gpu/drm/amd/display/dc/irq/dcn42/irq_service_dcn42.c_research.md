# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c

Purpose: DCN 4.2 IRQ service for dal-dev, using DCN 4.2 register offsets and the same modern four-active-pipe table style as DCN401.

Important APIs and functions: `to_dal_irq_source_dcn42()` maps standard display IDs, HPD/RX ext IDs, and DMCUB low-priority outbox. `irq_source_info_dcn42` contains HPD/RX 0 through 3, pflip/vblank/vupdate/vline0/1/2 0 through 3, DMCUB OUTBOX1, and dummy placeholders for unsupported enum slots. `dal_irq_service_dcn42_create()` is the factory.

Control flow: constructor installs the static table and mapper. Runtime set/ack uses the shared service. VLINE1/2 table entries are available by explicit `dc_irq_source` use even though the translator maps only vertical interrupt 0 source IDs.

State and persistence: static const table and allocated service object. Hardware interrupt enable and clear bits persist in MMIO.

Dependencies and integration points: DCN 4.2 offsets/masks, DCE110 shared IRQ service declarations, and DCN interrupt source IDs. The header includes DCE110 service definitions instead of the local generic `irq_service.h`, which still provides the needed shared types through that path.

Risks: dal-dev comment suggests this may be branch- or development-specific. Include-path difference from other DCN headers should be kept intentional. Table/hardware resource mismatch around four active pipes and HPDs should be validated.

Test signals: compile for DCN42 register macros, then runtime HPD, DMCUB outbox, vblank, page flip, and vline0/1/2 tests on DCN4.2 hardware.
