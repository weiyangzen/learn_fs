# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c

Purpose: DCN 3.2 IRQ service with support for additional OTG vertical interrupt lines (`VLINE1` and `VLINE2`) and DMCUB low-priority outbox.

Important APIs and functions: `to_dal_irq_source_dcn32()` maps standard vblank/vline0/pflip/vupdate/HPD/RX and DMCUB outbox source IDs. The table includes callback structs and macros for vline0, vline1, and vline2, although source translation only maps vertical interrupt 0 IDs directly. `dal_irq_service_dcn32_create()` is the factory.

Control flow: most callers use translation for interrupt dispatch; consumers that explicitly enable `DC_IRQ_SOURCE_DC*_VLINE1` or `DC*_VLINE2` can use table entries even though they are not returned by the current translator. Shared generic set/ack programs the OTG vertical interrupt control registers.

State and persistence: static const table and heap service object. VLINE1/2 enable state is persistent hardware state in OTG vertical interrupt 1/2 control registers.

Dependencies and integration points: DCN 3.2 register headers, DCE110 helpers, DCN IRQ source IDs, and shared IRQ service. Integration includes more precise scanline interrupt programming for timing-sensitive display operations.

Risks: mismatch between translation coverage and table coverage can confuse new call sites. Only four active pflip entries are present while enum ranges contain six. DMCUB OUTBOX1 mapping must match firmware usage.

Test signals: vline0/1/2 programming tests, vblank/page flip, DMCUB outbox notification, and HPD. Compile coverage catches missing vertical interrupt register symbols.
