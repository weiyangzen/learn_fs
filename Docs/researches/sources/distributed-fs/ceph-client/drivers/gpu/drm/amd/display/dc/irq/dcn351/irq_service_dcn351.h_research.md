# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.h

Purpose: compact factory header for DCN 3.5.1 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn351_create()`.

Control flow and integration: included by DCN351 ASIC setup code.

State and persistence: no storage; all state is in the C implementation and hardware registers.

Dependencies, risks, and test signals: depends on `../irq_service.h`; compile coverage validates the contract.
