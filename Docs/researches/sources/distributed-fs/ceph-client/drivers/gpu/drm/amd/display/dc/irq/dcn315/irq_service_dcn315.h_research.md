# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.h

Purpose: exposes the DCN 3.1.5 IRQ service constructor.

Important APIs/types/functions: declares `dal_irq_service_dcn315_create()`.

Control flow and integration: ASIC initialization includes this header to instantiate the DCN315 table.

State and persistence: no state in the header.

Dependencies, risks, and test signals: synchronized build with the C file is the key validation.
