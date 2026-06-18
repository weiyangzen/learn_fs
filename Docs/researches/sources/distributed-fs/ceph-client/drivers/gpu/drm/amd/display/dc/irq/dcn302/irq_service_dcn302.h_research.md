# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.h

Purpose: declares the DCN 3.0.2 IRQ service constructor.

Important APIs/types/functions: `dal_irq_service_dcn302_create(struct irq_service_init_data *init_data)`.

Control flow and integration: used by ASIC factory code to bind DCN302-specific interrupt source mapping.

State and persistence: header contains no storage.

Dependencies, risks, and test signals: depends on `../irq_service.h`; build coverage catches prototype drift.
