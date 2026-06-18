# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.h

Purpose: declares the DCN 3.1.4 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn314_create()`.

Control flow and integration: used by ASIC setup to select the DCN314 mapper/table.

State and persistence: no state.

Dependencies, risks, and test signals: depends on shared IRQ types; compile coverage catches ABI drift.
