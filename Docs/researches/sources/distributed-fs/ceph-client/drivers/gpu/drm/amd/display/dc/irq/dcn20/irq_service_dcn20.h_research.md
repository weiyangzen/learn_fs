# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.h

Purpose: public factory header for the DCN 2.0 interrupt service.

Important APIs/types/functions: declares `struct irq_service *dal_irq_service_dcn20_create(struct irq_service_init_data *init_data);` and includes the shared `../irq_service.h` definitions for `irq_service`, `irq_source_info`, and initialization data.

Control flow and integration: ASIC bring-up code includes this header and calls the create function to obtain an initialized service whose callbacks and table are implemented in `irq_service_dcn20.c`.

State and persistence: this header owns no state. Its main contract is that callers must later destroy the returned heap object through the shared IRQ service lifetime path.

Dependencies, risks, and test signals: depends on the shared IRQ service ABI. Any signature change must stay synchronized with the C file and ASIC factory callers; build coverage is the primary test signal.
