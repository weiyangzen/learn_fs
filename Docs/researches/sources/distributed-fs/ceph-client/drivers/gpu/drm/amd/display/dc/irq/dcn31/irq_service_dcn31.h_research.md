# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.h

Purpose: public interface for constructing the DCN 3.1 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn31_create()`.

Control flow and integration: included by DCN31 ASIC factory/resource setup code.

State and persistence: header has no storage.

Dependencies, risks, and test signals: relies on the shared `irq_service.h` ABI; build coverage is the primary signal.
