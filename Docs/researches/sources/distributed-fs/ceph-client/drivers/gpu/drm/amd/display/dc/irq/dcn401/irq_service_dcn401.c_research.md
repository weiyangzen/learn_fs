# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c

Purpose: DCN 4.0.1 IRQ service with compile-time DCN 4.1 register offsets, DMCUB low-priority outbox, and active vline0/vline1/vline2 table entries.

Important APIs and functions: `to_dal_irq_source_dcn401()` maps six standard display source IDs, HPD/RX ext IDs, and DMCUB outbox. `irq_source_info_dcn401` has four HPD/RX entries, four pflip entries, four vblank/vupdate/vline0/vline1/vline2 entries, dummy entries for unsupported PFLIP5/6 and some vline slots, and DMCUB OUTBOX1. `dal_irq_service_dcn401_create()` constructs the service.

Control flow: source translation covers vline0 only; vline1/vline2 are exposed for explicit enable/ack by their `dc_irq_source` values. Generic set/ack writes register masks for most entries; HPD uses the shared polarity-aware ack helper.

State and persistence: static const table and heap wrapper. Hardware state is persisted in HPD, HUBPREQ, OTG, and DMCUB registers.

Dependencies and integration points: DCN 4.1.0 offset/mask headers, DCN IRQ source IDs, DCE110 helpers, and shared IRQ service. Integrates newer multi-vline timing sources with the common interrupt API.

Risks: `DCN_BASE__INST0_SEG2` override and compile-time base expansion are sensitive to register-map changes. Only four HPD/RX and pflip instances are active despite enum and translation cases for six IDs. VLINE1/2 availability should be tied to hardware resource caps.

Test signals: DCN401 hardware tests for vline0/1/2 programming, DMCUB outbox, HPD/RX, vblank, and page flips; build checks for DCN 4.1 register macro drift.
