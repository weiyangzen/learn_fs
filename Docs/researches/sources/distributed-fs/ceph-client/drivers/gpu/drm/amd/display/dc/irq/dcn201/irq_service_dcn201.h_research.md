# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.h

Purpose: exposes the DCN 2.0.1 interrupt service constructor.

Important APIs/types/functions: includes `../irq_service.h` and declares `dal_irq_service_dcn201_create()`.

Control flow and integration: display ASIC factory code calls this function when the detected IP version needs the DCN201 IRQ table and source mapper.

State and persistence: header-only declaration; no storage.

Dependencies, risks, and test signals: ABI drift with the C implementation or factory code is caught at build time. Runtime validation belongs to the DCN201 C file and shared IRQ service.
