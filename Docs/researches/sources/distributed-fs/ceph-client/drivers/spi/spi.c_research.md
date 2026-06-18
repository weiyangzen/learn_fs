# sources/distributed-fs/ceph-client/drivers/spi/spi.c

## Purpose

`spi.c` is the Linux SPI core implementation. It owns the `spi_bus_type`, controller classes, SPI device allocation and registration, board-info and firmware-node enumeration, transfer validation, message optimization, queued and direct transfer execution, DMA mapping, statistics, bus locking, suspend/resume gates, and the common synchronous/asynchronous API used by protocol drivers. It is the central integration layer between SPI controller drivers, SPI device drivers, firmware descriptions, PM runtime, DMA, GPIO chip-select handling, and userspace-visible driver binding.

## Important APIs, Types, And Functions

Primary exported registration APIs include `__spi_register_driver()`, `spi_alloc_device()`, `spi_add_device()`, `spi_new_device()`, `spi_unregister_device()`, `spi_register_board_info()`, `__spi_alloc_controller()`, `__devm_spi_alloc_controller()`, `spi_register_controller()`, `devm_spi_register_controller()`, and `spi_unregister_controller()`. Matching and device data helpers include `spi_get_device_id()` and `spi_get_device_match_data()`.

Transfer APIs include `spi_setup()`, `spi_async()`, `spi_sync()`, `spi_sync_locked()`, `spi_bus_lock()`, `spi_bus_unlock()`, `spi_write_then_read()`, `spi_finalize_current_transfer()`, and `spi_finalize_current_message()`. Message preparation helpers include `spi_optimize_message()`, `spi_unoptimize_message()`, `devm_spi_optimize_message()`, `spi_split_transfers_maxsize()`, and `spi_split_transfers_maxwords()`. Timing helpers include `spi_delay_to_ns()`, `spi_delay_exec()`, `spi_transfer_cs_change_delay_exec()`, `spi_take_timestamp_pre()`, and `spi_take_timestamp_post()`.

Important internal state lives in `struct spi_controller`, `struct spi_device`, `struct spi_message`, `struct spi_transfer`, `struct spi_res`, `struct spi_replaced_transfers`, board-info list nodes, per-CPU `struct spi_statistics`, controller IDR state, queue state (`queue`, `cur_msg`, `running`, `busy`, `queue_empty`), chip-select cache (`last_cs`, `last_cs_index_mask`, `last_cs_mode_high`), and DMA scratch buffers (`dummy_tx`, `dummy_rx`).

## Control Flow And State

Core initialization runs at `postcore_initcall(spi_init)`. It allocates a small shared DMA-safe buffer for `spi_write_then_read()`, registers the SPI bus, registers host and optional target classes, and attaches OF/ACPI dynamic reconfiguration notifiers. Controllers are allocated with initialized locks, queues, defaults, class membership, parent links, and private data alignment. `spi_register_controller()` validates controller methods, assigns a fixed or dynamic bus number via `spi_controller_idr`, initializes completions and chip-select cache, optionally obtains chip-select GPIO descriptors, publishes the controller device, starts the queued pump when needed, matches board-info entries, and enumerates OF/ACPI children.

SPI devices are created from board info, OF child nodes, ACPI `SpiSerialBus` resources, ancillary-device requests, or dynamic firmware reconfiguration. `__spi_add_device()` validates chip-select ranges and collisions, maps GPIO descriptors, applies initial `__spi_setup()`, and then calls `device_add()`. `spi_unregister_device()` clears OF/ACPI populated/enumerated state, removes software nodes, deletes the device, invokes controller cleanup, and releases the object.

Transfer submission starts with validation and optional optimization. `__spi_validate()` rejects empty messages, invalid half-duplex combinations, unsupported bits-per-word, bad word alignment, speed values outside controller limits, incompatible multi-lane flags, DTR requests without controller support, and missing offload capability. `spi_split_transfers()` may replace transfers to emulate `SPI_CS_WORD` or respect max transfer size. Resource-backed replacements are undone during unoptimization or message finalization.

Queued controllers use `spi_queued_transfer()` to append messages under `queue_lock`; `spi_pump_messages()` drains them from a kthread worker. `__spi_pump_transfer_message()` powers the controller when `auto_runtime_pm` is set, calls `prepare_transfer_hardware()`, `prepare_message()`, DMA-maps transfers, sets completion ordering flags, invokes the controller's `transfer_one_message()`, and waits when completion may happen asynchronously. The default `spi_transfer_one_message()` asserts chip select, accounts statistics, synchronizes DMA, invokes `transfer_one()`, waits with a clock-derived timeout when needed, handles PIO fallback after DMA no-start failures, applies delays, handles `cs_change`, updates `actual_length`, deasserts chip select, calls controller error handling, and finalizes the message.

Synchronous transfers use a fast noqueue path when the queue is empty and `must_async` is false, otherwise they queue an async message and wait for a completion. Bus locking uses `bus_lock_mutex` plus `bus_lock_spinlock` and `bus_lock_flag` to exclude ordinary async submissions while allowing `spi_sync_locked()` from the lock holder. Suspend stops the queue and marks `SPI_CONTROLLER_SUSPENDED`; resume clears the flag and restarts the queue.

## State And Persistence Behavior

Runtime state is in kernel objects, not persistent storage. Persistent-ish board information from `spi_register_board_info()` is intentionally kept in `board_list` forever so controller reloads recreate known devices. Controller IDs are tracked in an IDR until unregister. OF nodes use `OF_POPULATED`; ACPI devices use enumerated state and `ignore_parent` power flags. Device and controller statistics are per-CPU counters exposed through sysfs `statistics` groups. Message resources persist only for the life of an optimized or in-flight message and are released in reverse order.

## Dependencies And Integration Points

The file integrates with driver core bus/class/device registration, OF and ACPI enumeration, GPIO descriptors, DMA mapping and scatterlists, DMAengine channel devices, PM runtime and PM domains, kthread workers, completion and lock primitives, PTP timestamp helpers, firmware-node APIs, SPI memory/offload interfaces, tracepoints, sysfs attributes, and dynamic OF/ACPI reconfiguration notifiers. Controller drivers plug in through `struct spi_controller` callbacks such as `setup`, `cleanup`, `transfer`, `transfer_one`, `transfer_one_message`, `prepare_message`, `unprepare_message`, `optimize_message`, `unoptimize_message`, `set_cs`, `set_cs_timing`, `can_dma`, `handle_err`, and target-mode callbacks.

## Risks And Test Signals

High-risk areas are transfer finalization ordering, queue teardown, PM runtime balancing, DMA mapping fallback, chip-select polarity/caching, dynamic firmware-node add/remove races, and message optimization lifetime. A controller that calls `spi_finalize_current_message()` too early or too late can race with `cur_msg` access. Incorrect `can_dma()` behavior can leak mapped SG tables or require fallback while buffers are still DMA-mapped. Chip-select handling is subtle with GPIO descriptors, ACPI polarity rules, multiple logical chip selects, `SPI_CS_HIGH`, and `SPI_CONTROLLER_GPIO_SS`.

Useful test signals include SPI controller probe/remove with fixed and dynamic bus numbers, OF and ACPI child enumeration, dynamic overlay add/remove, board-info replay after controller reload, full-duplex and half-duplex validation failures, DMA and PIO fallback transfers, `SPI_CS_WORD` splitting, max-transfer splitting, synchronous noqueue and queued ordering, PM suspend/resume, bus lock exclusion, statistics sysfs counters, PTP timestamp warnings, and timeout/error paths with controller `handle_err()` coverage.
