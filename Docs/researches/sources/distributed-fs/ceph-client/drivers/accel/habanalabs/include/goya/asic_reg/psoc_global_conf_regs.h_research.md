# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/psoc_global_conf_regs.h

Purpose: defines 361 PSOC global configuration register addresses from `0xC4B000` to `0xC4BA44`. The map covers boot sequencing, persistent flops, scratchpads, semaphores, firmware/bootloader status, interrupt/status aggregation, target IDs, reset configuration, memory repair, trace address/user attributes, pin muxing, and pad controls.

Important APIs/types/functions: macro-only `mmPSOC_GLOBAL_CONF_*` addresses. Important groups include `NON_RST_FLOPS_*`, `SCRATCHPAD_0..31`, `COLD_RST_FLOPS_*`, `KMD_MSG_TO_CPU`, `CPU_BOOT_STATUS`, `TRACE_ADDR`, `TRACE_ARUSER`, `TRACE_AWUSER`, reset config registers, and `PAD_SEL_0..81`.

Control flow: boot and firmware code reads scratchpads/status registers to learn device state; reset code writes boot restart and reset config registers; CoreSight writes trace address/user registers; common register maps alias scratchpads to logical names such as hardware state, CPU boot errors, and update status.

State and persistence: the hardware state is intentionally persistent across parts of boot/reset. Scratchpads and cold/non-reset flops are host/firmware communication state, not temporary local variables.

Dependencies and integration: included by `goya_regs.h`; field masks are in `psoc_global_conf_masks.h`. `include/goya/asic_reg/goya_regs.h` aggregates it with other blocks, while higher-level `goya_reg_map.h` aliases scratchpad registers for common driver code.

Risks: register address mistakes break firmware handshakes, boot diagnostics, and reset flows. The large indexed pad/scratchpad ranges should remain mechanically generated to avoid off-by-one offsets. Host and firmware must agree on scratchpad numbering.

Test signals: device boot, firmware loading, KMD-to-CPU messaging, reset and warm reboot tests, CoreSight trace configuration, pad/pin mux validation, and firmware status/error reporting cover this map.
