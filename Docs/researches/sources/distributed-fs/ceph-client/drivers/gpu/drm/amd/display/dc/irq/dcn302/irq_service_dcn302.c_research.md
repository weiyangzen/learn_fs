# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c

Purpose: DCN 3.0.2 IRQ service variant. It resembles DCN30, including DMCUB high-priority OUTBOX0 support, but uses DCN 3.0.2 offset/mask headers.

Important APIs and functions: `to_dal_irq_source_dcn302()` maps six display timing and flip sources plus HPD/RX and high-priority DMCUB outbox. Macros build HPD, HPD RX, pflip, vupdate, vblank, vline0, and DMUB trace entries. `dal_irq_service_dcn302_create()` is the factory.

Control flow: translation and table-driven enable/ack match the shared IRQ service pattern. HPD ack uses polarity flipping; other functional entries use generic register set/ack because callbacks are NULL.

State and persistence: a static const table and heap `irq_service` wrapper. Hardware interrupt state is persistent in the selected MMIO registers until the service changes it.

Dependencies and integration points: depends on DCN 3.0.2 register headers, DCN interrupt source IDs, DCE110 helpers, and the shared IRQ framework. DMCUB OUTBOX0 integrates firmware-side notification into display interrupt routing.

Risks: register tables are hand-expanded by macros; source/index mismatches can silently route the wrong IRQ source. OUTBOX0 vs OUTBOX1 mismatch is the main firmware integration risk.

Test signals: successful creation on DCN302 hardware, DMCUB outbox delivery, page-flip/vblank/vline interrupts, and HPD/HPD RX events. Compilation validates offset/mask symbol availability.
