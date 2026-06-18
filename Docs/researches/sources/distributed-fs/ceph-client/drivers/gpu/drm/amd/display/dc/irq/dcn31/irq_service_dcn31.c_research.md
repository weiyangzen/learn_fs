# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c

Purpose: DCN 3.1 IRQ service with low-priority DMCUB outbox support and a mostly four-pipe table despite source translation cases for six standard display IDs.

Important APIs and functions: `to_dal_irq_source_dcn31()` maps vblank, vline0, pflip, vupdate, HPD/RX, and `DMCUB_OUTBOX_LOW_PRIORITY_READY_INT`. `irq_source_info_dcn31` defines HPD/RX entries for instances 0 through 4, pflip entries for 0 through 3, vupdate/vblank/vline0 entries for 0 through 5 in the static table, and DMCUB OUTBOX1 support.

Control flow: source translation feeds `dal_irq_service_set/ack()`. HPD uses shared polarity-aware ack; DMCUB and display timing entries rely on generic MMIO masks.

State and persistence: immutable IRQ table and heap service. Hardware interrupt enable/ack bits persist in DMCUB, OTG, HUBPREQ, and HPD registers.

Dependencies and integration points: uses DCN31 register offsets/masks, DCE110 helpers, and the common DCN interrupt ID header. DMCUB outbox integrates firmware events with display interrupts.

Risks: hardware instance count is easy to misread because source translation lists six pipes while pflip table entries only cover four active HUBP entries. Connector count appears five HPD/RX entries in the table. Callers should respect resource caps rather than infer from enum ranges.

Test signals: hotplug on all exposed connectors, page flip on active HUBPs, DMCUB outbox interrupts, and vblank/vline events under modeset and DPMS transitions.
