# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.h

Purpose: factory declaration for the DCN 3.0.3 interrupt service.

Important APIs/types/functions: declares `dal_irq_service_dcn303_create()`.

Control flow and integration: selected by ASIC-specific initialization when DCN303 register definitions are required.

State and persistence: no state.

Dependencies, risks, and test signals: includes the shared IRQ service contract; build tests catch C/header mismatch.
