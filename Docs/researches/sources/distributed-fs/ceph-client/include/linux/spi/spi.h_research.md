<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi.h

Purpose: This is the main Linux SPI core API. It defines SPI devices, protocol drivers, controllers, transfer/message objects, statistics, registration helpers, synchronous/asynchronous I/O helpers, board-info templates, DMA/timestamp/offload hooks, and message-resource management.

Important APIs/types/functions: Key types include `spi_device`, `spi_driver`, `spi_controller`, `spi_transfer`, `spi_message`, `spi_statistics`, `spi_delay`, `spi_board_info`, `spi_res`, and `spi_replaced_transfers`. Important APIs cover driver registration, controller allocation/registration, device allocation/add/remove, message init/add/free, `spi_async()`, `spi_sync()`, `spi_sync_transfer()`, `spi_write/read()`, `spi_write_then_read()`, bus lock/unlock, controller suspend/resume, transfer/message finalization, PTP timestamp helpers, message optimization, transfer splitting, and board-info registration.

Control flow: Protocol drivers configure `spi_device`, build `spi_message` lists of `spi_transfer` segments, then submit asynchronously or synchronously. Controller drivers either provide a raw `transfer()` queue entry point or use core queuing with `transfer_one_message()`/`transfer_one()`. The generic queue tracks `cur_msg`, completions, queue state, runtime PM, DMA mapping, chip-select state, error handling, and finalization callbacks.

State and persistence: `spi_controller` owns bus-wide locks, queues, current message, runtime PM flags, DMA channels, GPIO chip-select descriptors, stats, and controller capabilities. `spi_device` owns per-target mode, max speed, word size, CS mapping, lane maps, delays, IRQ, controller-private state, and per-device stats. `spi_message` and `spi_transfer` are caller-owned until completion.

Dependencies/integration: Integrates with the driver core, ACPI/OF firmware, GPIO descriptors, DMA engine, PTP timestamping, statistics/u64 sync, offload, spi-mem, board files, and UAPI SPI mode constants. Compile-time assertion prevents kernel-only mode bits from overlapping user-visible bits.

Risks and test signals: Risks include message/transfer lifetime violations, forgetting `spi_finalize_current_*()`, unsupported mode or bits-per-word, DMA alignment/size errors, chip-select timing mistakes, queue fast-path races, PTP timestamp quality issues, and offload misuse. Test with spi-loopback/spidev, sync/async stress, suspend/resume, GPIO CS and native CS, DMA/PIO fallback, transfer splitting, multi-CS/lane setups, stats counters, and controller unregister with queued messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi.h -->
