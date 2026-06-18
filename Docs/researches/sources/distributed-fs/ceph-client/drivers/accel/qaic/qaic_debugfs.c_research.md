# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.c

Purpose: provides QAIC debugfs visibility and the `QAIC_LOGGING` MHI bootlog receiver. It creates per-device debugfs files for firmware boot logs and per-DBC FIFO state.

Important APIs and types: public functions are `qaic_debugfs_init`, `qaic_bootlog_register`, and `qaic_bootlog_unregister`. Internal types are `bootlog_msg` for MHI receive buffers and work items, and `bootlog_page` for page-backed log storage.

Control flow: `qaic_debugfs_init` creates `bootlog` plus `dbcNNN/fifo_size` and `dbcNNN/queued` files. The bootlog MHI probe allocates an ordered workqueue, resets the log page list, prepares the channel, and queues a fixed pool of receive buffers. On each downlink completion, the callback null-terminates the string and queues work; `bootlog_log` appends it to page storage and requeues the buffer.

State and persistence: boot logs are kept in memory as devm-managed pages linked from `qdev->bootlog`, protected by `bootlog_mutex`. They survive while the device object survives but are reset when the logging channel probes again.

Dependencies and integration: uses debugfs, seq_file, MHI, devm page allocation, `qaic_data_get_fifo_info`, and `qaic_device` fields initialized by `qaic_drv.c`. Registration is conditional through `qaic_debugfs.h` and called from module init.

Risks and test signals: validate bootlog strings with short/empty transfers, page rollover, logging channel removal while work is queued, debugfs reads during reset, and `queued` behavior when MMIO reads return `U32_MAX`.
