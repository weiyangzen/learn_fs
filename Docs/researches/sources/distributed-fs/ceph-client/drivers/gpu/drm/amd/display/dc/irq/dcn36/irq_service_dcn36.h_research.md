# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.h

Purpose: declares the DCN 3.6 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn36_create()`.

Control flow and integration: selected by DCN36 ASIC initialization.

State and persistence: no state.

Dependencies, risks, and test signals: depends on shared IRQ service types; build coverage catches mismatches.
