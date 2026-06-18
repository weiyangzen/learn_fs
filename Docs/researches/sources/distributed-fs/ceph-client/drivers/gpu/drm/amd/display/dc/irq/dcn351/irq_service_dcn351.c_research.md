# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c

Purpose: DCN 3.5.1 IRQ service. It is a runtime-offset variant like DCN35, with the same broad source categories and DMCUB low-priority outbox support.

Important APIs and functions: `to_dal_irq_source_dcn351()` maps display timing/flip IDs, HPD/RX ext IDs, and DMCUB outbox. `dcn351_irq_init_part_1/2()` populate `irq_source_info_dcn351` through `REG_STRUCT`, using `ctx->dcn_reg_offsets`. `dal_irq_service_dcn351_create()` is the exported constructor.

Control flow: construction initializes the static mutable table for the current context, then shared source translation and set/ack paths use it. HPD ack uses `hpd0_ack()`, while pflip, vblank, vupdate, vline0, and DMCUB outbox use generic register masks.

State and persistence: static mutable IRQ table initialized at construction time plus one heap service object. Hardware register state persists across enable/ack calls.

Dependencies and integration points: DCN 3.5.1 offsets/masks, dynamic `dc_context` base offsets, DCE110 helper callbacks, and the common IRQ service. It is integrated where DCN351 ASIC resources are created.

Risks: same mutable-global table risk as DCN35 and DCN36. Source translation includes six display IDs, but initialization enables only four pflip/vblank/vline/vupdate instances and HPD/RX 0 through 4. Incorrect offset initialization can target wrong registers.

Test signals: register-address sanity checks after construction, DMCUB outbox delivery, HPD/RX events, and display timing interrupts under modeset/page flip.
