# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c

Purpose: DCN 3.5 IRQ service using runtime register base offsets from `ctx->dcn_reg_offsets` instead of compile-time DCN base constants.

Important APIs and functions: `to_dal_irq_source_dcn35()` maps six display source IDs, HPD/RX ext IDs, and DMCUB low-priority outbox. Unlike earlier static-table files, `dcn35_irq_init_part_1/2()` populate a mutable `irq_source_info_dcn35` array at construct time through `REG_STRUCT`. `dal_irq_service_dcn35_create()` allocates and constructs the service.

Control flow: constructor obtains `struct dc_context *ctx = init_data->ctx`, then expands table-init macros against `ctx->dcn_reg_offsets`. Runtime dispatch and enable/ack then follow the shared path. HPD ack is polarity-aware; other sources use generic MMIO writes.

State and persistence: `irq_source_info_dcn35` is a static mutable table initialized at service construction. This creates global process/module state rather than per-service table storage. Hardware state is in the normal interrupt registers.

Dependencies and integration points: DCN 3.5 register headers, `dc_context` register-offset configuration, DCE110 helpers, and shared IRQ service. This design integrates with ASICs whose base addresses are supplied dynamically.

Risks: static mutable initialization is not obviously concurrency-safe if multiple services with different contexts were constructed. Reinitialization with a different `ctx->dcn_reg_offsets` would overwrite the global table. The table activates four pflip/vblank/vline/vupdate instances and HPD/RX 0 through 4, while the translator recognizes six source IDs.

Test signals: construct-time tests should verify computed register addresses, especially on platforms with non-default offsets. Runtime signals are hotplug, DMCUB outbox, vblank/vline/vupdate, and page flips.
