# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.h

Purpose: declares the DCN 2.1 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn21_create()` returns a configured `struct irq_service` for DCN21.

Control flow and integration: included by ASIC-specific resource/factory code to select the DCN21 IRQ implementation.

State and persistence: no state in the header.

Dependencies, risks, and test signals: depends on the shared `irq_service.h` contract. Build coverage catches declaration/definition mismatch.
