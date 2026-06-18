# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.h

Purpose: public DCN 4.0.1 IRQ service factory declaration.

Important APIs/types/functions: declares `dal_irq_service_dcn401_create()`.

Control flow and integration: used by DCN401 ASIC setup to select this mapper/table.

State and persistence: no state.

Dependencies, risks, and test signals: shared IRQ ABI dependency; compile coverage validates declaration consistency.
