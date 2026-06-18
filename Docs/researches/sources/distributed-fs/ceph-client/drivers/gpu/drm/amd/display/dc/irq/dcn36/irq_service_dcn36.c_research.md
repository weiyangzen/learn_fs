# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c

Purpose: DCN 3.6 IRQ service. It follows the DCN351 runtime-offset construction pattern and provides low-priority DMCUB outbox plus standard display interrupt categories.

Important APIs and functions: `to_dal_irq_source_dcn36()` maps six vblank/vline0/pflip/vupdate IDs, HPD/RX ext IDs, and DMCUB outbox. `dcn36_irq_init()` populates the static mutable `irq_source_info_dcn36` table using `ctx->dcn_reg_offsets`. `dal_irq_service_dcn36_create()` allocates the service.

Control flow: constructor initializes table addresses from the current `dc_context`, then installs table and funcs. Runtime dispatch uses shared translation and table-driven generic ack/set, except HPD ack uses `hpd0_ack()`.

State and persistence: the static mutable table is process/module-wide and rewritten during construction. Hardware interrupt masks persist in registers. The heap service only stores pointers.

Dependencies and integration points: DCN 3.6 offsets/masks, DCE110 helpers, `dc_context` dynamic offsets, DCN interrupt source IDs, and shared IRQ service. It is the interrupt bridge for DCN36 display resources.

Risks: global mutable table can be corrupted by multiple contexts or unexpected repeated construction. Table initialization enables only a subset of translated instances, so resource capability checks are required. DMCUB OUTBOX1 mapping must match firmware IRQ routing.

Test signals: verify table address values after construction, HPD and DMCUB interrupts, and vblank/page flip behavior on active pipes.
