# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c

Purpose: DCN 3.0 IRQ service for full six-pipe display configurations, with DMCUB high-priority outbox support represented as `DC_IRQ_SOURCE_DMCUB_OUTBOX0`.

Important APIs and functions: `to_dal_irq_source_dcn30()` maps six vblank, six vline0, six pflip, six vupdate, HPD/RX, and `DMCUB_OUTBOX_HIGH_PRIORITY_READY_INT`. `dmub_trace_int_entry()` programs `DMCUB_OUTBOX0_READY_INT_EN/ACK`. `dal_irq_service_dcn30_create()` allocates and constructs the service.

Control flow: source IDs enter through the common dispatcher, are converted to `dc_irq_source`, and are serviced by generic enable/ack or the HPD polarity-aware ack helper. DMCUB trace/outbox is handled as another table entry.

State and persistence: the static table is immutable and the service object only holds pointers. Hardware state lives in DMCUB, OTG, HUBPREQ, and HPD registers.

Dependencies and integration points: includes DCN 3.0 offsets/masks, DCN IRQ source IDs, and DCE110 helpers. This file connects DCN30 display interrupt routing to the DRM AMD display core and DMUB trace/outbox processing.

Risks: DMCUB high-priority OUTBOX0 naming differs from DCN21 OUTBOX1. Incorrect mapping can make firmware trace/outbox events invisible. Six-pipe table entries should only be selected for hardware exposing the matching register instances.

Test signals: DMCUB outbox interrupt handling, vblank/page-flip interrupt counters, hotplug events, and link training paths that rely on DMUB notification. Compile-time register macro availability is a key regression signal.
