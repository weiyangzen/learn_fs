# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c

Purpose: DCN 2.1 interrupt service, extending the DCN20 model with a DMCUB low-priority outbox interrupt source.

Important APIs and functions: `to_dal_irq_source_dcn21()` maps standard DCN display events plus `DCN_1_0__SRCID__DMCUB_OUTBOX_LOW_PRIORITY_READY_INT` to `DC_IRQ_SOURCE_DMCUB_OUTBOX`. `dmub_outbox_int_entry()` defines the DMCUB enable/ack registers using `DMCUB_OUTBOX1_READY_INT_EN` and `DMCUB_OUTBOX1_READY_INT_ACK`. `dal_irq_service_dcn21_create()` is the exported factory.

Control flow: interrupt source translation selects one of HPD/RX, vblank, vline0, pflip, vupdate, or DMCUB outbox. The shared IRQ service acknowledges/enables via table entries. DMCUB outbox uses generic ack/set because its callbacks are NULL.

State and persistence: static const IRQ table plus heap service object. Persistent effects are the programmed DMCUB interrupt enable/ack state and the normal OTG/HUBP/HPD interrupt control registers.

Dependencies and integration points: depends on DCN 2.1 offset/mask headers, DMU base offsets, DCN interrupt source IDs, DCE110 shared helpers, and the DMCUB interrupt register definitions. It integrates display firmware mailbox readiness with the same `dc_irq_source` dispatch path as display pipe events.

Risks: DMCUB outbox low-priority vs high-priority mapping differs across generations; confusing OUTBOX0 and OUTBOX1 can break firmware notifications. The table includes five HPD/RX entries and only four active pflip entries despite source translation cases for six pflip IDs, so hardware capability assumptions must be checked.

Test signals: verify DMCUB outbox IRQs wake the DMUB service, hotplug works on supported connectors, and vblank/page-flip events remain stable. Unit-level confidence is mostly compile-time macro coverage.
