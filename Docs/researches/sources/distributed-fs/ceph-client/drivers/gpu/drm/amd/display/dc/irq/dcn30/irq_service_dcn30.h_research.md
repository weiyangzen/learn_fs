# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.h

Purpose: public declaration for creating a DCN 3.0 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn30_create()` and imports the shared IRQ service definitions.

Control flow and integration: ASIC detection code includes this header to instantiate the DCN30-specific source mapper and register table.

State and persistence: no header state.

Dependencies, risks, and test signals: declaration must match `irq_service_dcn30.c`; build testing is the relevant signal.
