# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.c

Purpose: implements QAIC subsystem-restart handling on the `QAIC_SSR` MHI channel. It tracks DBC reset state, acknowledges firmware SSR events, downloads per-DBC crashdump tables and memory chunks, publishes completed dumps through `dev_coredumpv`, and resets the SoC if dump collection becomes inconsistent.

Important APIs and types: exported functions are `qaic_ssr_init`, `qaic_ssr_register`, `qaic_ssr_unregister`, and `qaic_clean_up_ssr`. Main wire types are `ssr_event`, `ssr_debug_transfer_info`, `ssr_memory_read`, `ssr_memory_read_rsp`, and done/response variants. Runtime state is `ssr_resp`, `ssr_crashdump`, and `ssr_dump_info`.

Control flow: probe prepares the channel and queues a small command receive buffer. `ssr_worker` handles `SSR_EVENT` state transitions, `DEBUG_TRANSFER_INFO` negotiation, and transfer-done responses. Crashdump collection first allocates a table buffer from firmware-provided address/length, reads the table through repeated `MEMORY_READ` commands, allocates a metadata+table+dump image, then walks each table entry chunk by chunk. Completion sends `DEBUG_TRANSFER_DONE`; a successful done response publishes the dump.

State and persistence: `qdev->ssr_dbc` marks the DBC blocked by SSR; `qdev->ssr_mhi_buf` is one preallocated crashdump transfer buffer. DBC sysfs states move through before/after shutdown and power-up. Completed dumps are handed to devcoredump; temporary buffers are freed or devm-managed.

Dependencies and integration: calls `qaic_dbc_enter_ssr`, `qaic_dbc_exit_ssr`, `release_dbc`, `set_dbc_state`, MHI queueing, DRM managed allocation, and devcoredump.

Risks and test signals: key risks are trusting firmware lengths, freeing the reusable memory-read request at the correct time, handling AFTER_POWER_UP while a dump is active, and reset escalation on protocol errors. Test table length validation, chunk boundaries, MHI UL/DL failures, concurrent event ordering, devcoredump ownership, and device reset cleanup.
