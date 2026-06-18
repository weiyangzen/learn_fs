# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.h

Purpose: declares the DCN 3.5 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn35_create()`.

Control flow and integration: used by DCN35 factory code; the C file performs runtime table initialization from `dc_context`.

State and persistence: no header state.

Dependencies, risks, and test signals: shared IRQ ABI dependency. Build coverage catches signature drift; runtime validation belongs to the C implementation.
