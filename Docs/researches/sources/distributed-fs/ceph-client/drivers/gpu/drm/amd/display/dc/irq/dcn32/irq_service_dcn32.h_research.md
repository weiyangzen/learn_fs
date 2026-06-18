# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.h

Purpose: factory header for DCN 3.2 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn32_create()`.

Control flow and integration: selected by DCN32 ASIC initialization to install the DCN32 IRQ source mapper and register table.

State and persistence: no state.

Dependencies, risks, and test signals: shared IRQ ABI dependency; build coverage validates the declaration.
