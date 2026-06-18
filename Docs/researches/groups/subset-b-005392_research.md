# Research: subset-b-005392

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spidev.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spidev.c

## Purpose

`spidev.c` implements the generic userspace character-device interface for selected SPI devices. It exposes `/dev/spidevB.C` nodes backed by the SPI core so applications can issue simple read/write half-duplex transfers or full `SPI_IOC_MESSAGE()` transfer arrays without a dedicated kernel protocol driver.

## Important APIs, Types, And Functions

`struct spidev_data` tracks the character device number, per-device SPI lock, underlying `struct spi_device *`, list linkage, open-user count, open-time TX/RX bounce buffers, and current speed override. Global state includes the reserved major `153`, `N_SPI_MINORS`, the `minors` bitmap, `device_list`, `device_list_lock`, and module parameter `bufsiz`.

File operations are `spidev_read()`, `spidev_write()`, `spidev_ioctl()`, optional `spidev_compat_ioctl()`, `spidev_open()`, and `spidev_release()`. Transfer helpers are `spidev_sync_unlocked()`, `spidev_sync_write()`, `spidev_sync_read()`, `spidev_message()`, and `spidev_get_ioc_message()`. Driver lifecycle uses `spidev_probe()`, `spidev_remove()`, `spidev_init()`, and `spidev_exit()`.

## Control Flow And State

Module init registers the character major, registers the `spidev` class, and registers an SPI driver with explicit SPI IDs, OF compatible strings, and development-only ACPI IDs. Probe rejects direct `"spidev"` DT compatibles through `spidev_of_check()`, allocates `spidev_data`, finds a free minor, creates a device node named from controller bus and chip select, links the instance into `device_list`, records the default speed, and stores driver data on the SPI device.

Open locates the `spidev_data` by device number under `device_list_lock`, lazily allocates one TX and one RX bounce buffer of `bufsiz`, increments the user count, and stores the object in `file->private_data`. Read and write reject requests larger than `bufsiz`, lock `spi_lock`, check whether remove has nulled `spidev->spi`, and run a single SPI transfer using the bounce buffer. `SPI_IOC_MESSAGE()` copies a user transfer array, builds a kernel `spi_message`, allocates aligned slices from the bounce buffers for each TX/RX transfer, copies TX data from userspace, calls `spi_sync()`, then copies RX data back.

IOCTL mode writes save old state, mutate `spi->mode`, `bits_per_word`, or `max_speed_hz`, call `spi_setup()`, and restore on failure. Speed writes store a per-file-interface speed in `spidev->speed_hz` while restoring `spi->max_speed_hz` to the original controller-facing value after setup. Remove prevents new opens by unlinking from `device_list`, sets `spidev->spi = NULL` under `spi_lock` so existing descriptors return `-ESHUTDOWN`, destroys the device node, frees the minor, and frees the object only when no file descriptors remain.

## State And Persistence Behavior

No settings are persistent across driver unbind or reboot. Runtime mode changes modify the underlying `spi_device` while the device exists. Bounce buffers exist only while at least one descriptor is open. Minor numbers are reused dynamically and depend on probe order; udev or mdev is expected to create/remove nodes from class events.

## Dependencies And Integration Points

This file depends on the SPI core API (`spi_sync()`, `spi_setup()`, `spi_target_abort()` in target builds), Linux character-device registration, device classes, user-copy helpers, compat pointer conversion, module parameters, and firmware matching tables. It intentionally limits production DT use to hardware-specific compatible strings and warns for generic development ACPI IDs.

## Risks And Test Signals

Risks include exposing raw bus access that can disrupt other devices through mode changes such as `SPI_CS_HIGH`, `SPI_NO_CS`, or three-wire settings; incorrect userspace transfer sizes causing buffer overflow if `bufsiz` accounting regresses; removal races with active file descriptors; and compat ioctl pointer truncation mistakes. Useful tests are repeated open/close with lazy buffer allocation, read/write and multi-transfer ioctl paths, `bufsiz` overflow rejection, mode/speed/bits setup rollback on controller rejection, device removal while descriptors are active, minor exhaustion, compat `SPI_IOC_MESSAGE()`, and target-mode release abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spidev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/spmi/Kconfig

## Purpose

`drivers/spmi/Kconfig` defines the build-time configuration menu for SPMI support and the platform controller drivers in this tree. It gates the common SPMI framework and selects which vendor controller implementations are built.

## Important APIs, Types, And Functions

The top-level `menuconfig SPMI` is a tristate that enables System Power Management Interface support. Child symbols are `SPMI_APPLE`, `SPMI_HISI3670`, `SPMI_MSM_PMIC_ARB`, and `SPMI_MTK_PMIF`. The Hisilicon and Qualcomm options select `IRQ_DOMAIN_HIERARCHY`; controller options depend on their architecture families or `COMPILE_TEST`, and several also depend on `HAS_IOMEM`.

## Control Flow And State

There is no runtime control flow. The file controls compilation and module availability. Enabling `SPMI` exposes the child menu; disabling it excludes the common framework, devres helpers, and all listed controller drivers through the companion Makefile.

## State And Persistence Behavior

The selected values persist in the kernel build configuration. `SPMI_MSM_PMIC_ARB` defaults to enabled on Qualcomm builds; the other platform drivers require explicit selection or dependency-driven builds.

## Dependencies And Integration Points

The symbols map directly to object selections in `drivers/spmi/Makefile`. `IRQ_DOMAIN_HIERARCHY` is selected for controllers that provide hierarchical interrupt domains. Architecture dependencies prevent accidental platform-driver exposure except for compile-test coverage.

## Risks And Test Signals

Risks are mostly configuration-level: missing `HAS_IOMEM` or IRQ-domain selections can break builds, overly narrow dependencies can hide compile coverage, and overly broad defaults can build unusable platform drivers. Test signals are `allmodconfig`, platform defconfig, `COMPILE_TEST` builds for Apple/Hisilicon/MediaTek/Qualcomm paths, and checking that each enabled symbol pulls the expected object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/spmi/Makefile

## Purpose

`drivers/spmi/Makefile` maps SPMI Kconfig symbols to the common framework, devres helper, and platform controller object files.

## Important APIs, Types, And Functions

The file builds `spmi.o` and `spmi-devres.o` when `CONFIG_SPMI` is enabled. It conditionally builds `spmi-apple-controller.o`, `hisi-spmi-controller.o`, `spmi-pmic-arb.o`, and `spmi-mtk-pmif.o` from the vendor-specific symbols.

## Control Flow And State

There is no runtime control flow. Kbuild uses the `obj-$(CONFIG_...)` assignments to include objects built-in or as modules according to the tristate state of each symbol.

## State And Persistence Behavior

Build output changes according to `.config`; the Makefile itself stores no runtime state. Because `spmi-devres.o` follows `CONFIG_SPMI`, managed allocation/add APIs are available whenever the framework is built.

## Dependencies And Integration Points

This file integrates with `drivers/spmi/Kconfig` and the kernel build system. It also implies that vendor drivers depend on the common SPMI framework either directly through `CONFIG_SPMI` visibility or through the menu hierarchy.

## Risks And Test Signals

Risks are missing object mappings after adding a Kconfig symbol, accidentally building helper code without the framework, or stale object names after file renames. Test signals are Kbuild coverage for each SPMI tristate as built-in and module, and module alias/probe checks for the selected platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/hisi-spmi-controller.c -->
# sources/distributed-fs/ceph-client/drivers/spmi/hisi-spmi-controller.c

## Purpose

`hisi-spmi-controller.c` implements the Hisilicon Kirin 970 / Hi3670 SPMI controller driver. It translates SPMI framework read/write opcodes into the controller's APB command, status, write-data, and read-data registers for a configured hardware channel.

## Important APIs, Types, And Functions

`struct spmi_controller_dev` stores the framework controller, parent device, MMIO base, spinlock, and selected channel. Register constants define per-channel and per-slave offsets, command fields, data-register layout, transaction-done and fail bits, timeout, and the maximum transfer size of 16 bytes.

Main functions are `spmi_controller_wait_for_done()`, `spmi_read_cmd()`, `spmi_write_cmd()`, and `spmi_controller_probe()`. Driver registration uses `spmi_controller_init()` at `postcore_initcall()` and `spmi_controller_exit()` at module exit. The OF match table binds `"hisilicon,kirin970-spmi-controller"`.

## Control Flow And State

Probe allocates a devres-managed SPMI controller with private driver data, maps the platform MMIO resource, reads the `hisilicon,spmi-channel` property, initializes the spinlock, installs `read_cmd` and `write_cmd`, and adds the controller through `devm_spmi_controller_add()`. Runtime transfers serialize through `spmi_controller->lock`.

Read commands validate byte count and opcode, map SPMI framework opcodes to controller command types, pack enable/type/length/slave/address into the command register, write it, poll the status register until `SPMI_APB_TRANS_DONE`, check `SPMI_APB_TRANS_FAIL`, then read up to four 32-bit data registers. Data words are converted from big-endian register order before copying into the caller buffer.

Write commands validate byte count and opcode, copy caller bytes into 32-bit chunks, write big-endian data words to write-data registers, issue the packed command, and poll for completion. Both read and write paths hold the spinlock across register programming and polling, so transactions on a controller channel are strictly serialized.

## State And Persistence Behavior

The selected channel and mapped base persist for the platform device lifetime. No state is stored outside driver memory and hardware registers. The hardware status is polled per transaction; there is no IRQ-driven completion path in this driver.

## Dependencies And Integration Points

The driver depends on platform resources, OF properties, MMIO accessors, spinlocks, delay polling, and the SPMI framework callbacks. It uses devres helpers from `spmi-devres.c` for controller lifetime management.

## Risks And Test Signals

Risks include byte-count edge cases because `(bc - 1)` is encoded without an explicit zero-length rejection, endian or partial-word copying mistakes, long spinlock hold time during polling, stale status bits if hardware requires explicit clearing not visible here, and incorrect channel selection from firmware. Useful tests are probing with missing MMIO or channel properties, read/write opcodes for normal/ext/ext-long accesses, 1/4/5/16-byte transfers, invalid SID/opcode/length handling, transaction-fail injection, timeout behavior, concurrent SPMI clients, and endianness checks against known PMIC registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/hisi-spmi-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-apple-controller.c -->
# sources/distributed-fs/ceph-client/drivers/spmi/spmi-apple-controller.c

## Purpose

`spmi-apple-controller.c` implements the Apple SoC SPMI controller used on Apple Silicon platforms such as t8103. It provides minimal read and write callbacks for the SPMI framework using a command register, response FIFO register, and status polling.

## Important APIs, Types, And Functions

`struct apple_spmi` stores the MMIO register base. Register constants describe status, command, and response offsets plus the RX FIFO empty bit. `apple_spmi_pack_cmd()` encodes opcode, SID, address, length, and an enable/control bit. Runtime helpers are `apple_spmi_wait_rx_not_empty()`, `spmi_read_cmd()`, `spmi_write_cmd()`, and `apple_spmi_probe()`.

## Control Flow And State

Probe allocates a devres-managed SPMI controller, maps the first platform MMIO resource, assigns the OF node to the controller device, sets `read_cmd` and `write_cmd`, and adds the controller. Reads write a packed command, wait until the RX FIFO has a response, discard the reply status word, and then drain response words into the caller buffer a byte at a time. Writes write the packed command, stream payload bytes in 32-bit little-endian chunks through the command register, wait for a response, and discard the status word.

## State And Persistence Behavior

The only persistent software state is the MMIO base stored for the platform device lifetime. Transactions are synchronous and polling-based. The code does not keep an explicit software lock, so serialization relies on the SPMI core or the controller being safe for framework callback concurrency.

## Dependencies And Integration Points

The driver integrates with platform-device probing, `devm_platform_ioremap_resource()`, `readl_poll_timeout()`, OF matching for `"apple,t8103-spmi"` and `"apple,spmi"`, and the SPMI framework's devres-managed controller lifecycle.

## Risks And Test Signals

Risks include the absence of a local transfer lock, no explicit opcode/length validation beyond what the core may provide, a suspicious bitwise `&` in the write-loop condition where logical `&&` would be conventional, and limited response-status interpretation because status words are discarded rather than decoded. Test signals are probe on supported Apple SoCs, reads and writes of 1 through multiword lengths, RX FIFO timeout handling, concurrent SPMI client traffic, invalid opcode/length propagation from the core, and checking whether failed SPMI status replies are observable elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-apple-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-devres.c -->
# sources/distributed-fs/ceph-client/drivers/spmi/spmi-devres.c

## Purpose

`spmi-devres.c` provides device-managed wrappers for SPMI controller allocation and registration. It lets platform drivers tie `spmi_controller_put()` and `spmi_controller_remove()` to parent-device devres cleanup instead of open-coding unwind paths.

## Important APIs, Types, And Functions

The exported APIs are `devm_spmi_controller_alloc()` and `devm_spmi_controller_add()`. Release callbacks are `devm_spmi_controller_release()` for controller references and `devm_spmi_controller_remove()` for registered controllers.

## Control Flow And State

`devm_spmi_controller_alloc()` allocates a devres slot containing a controller pointer, calls `spmi_controller_alloc(parent, size)`, stores the returned pointer, and adds the release action to the parent. If allocation fails, it frees the devres slot and returns the framework error pointer.

`devm_spmi_controller_add()` allocates a second devres slot, calls `spmi_controller_add(ctrl)`, and records a remove action only after successful registration. On add failure, it frees the devres slot and returns the error. During parent-device teardown, devres unwinds in reverse order, removing the registered controller and then dropping the allocation reference.

## State And Persistence Behavior

The managed state is the controller pointer stored in parent devres records. No hardware state is touched here. Lifetime ordering depends on normal devres LIFO cleanup.

## Dependencies And Integration Points

This file depends on the SPMI core allocation, add, remove, and put APIs plus generic devres. Platform drivers such as the Hisilicon, Apple, and MediaTek SPMI controllers use these helpers to reduce manual error paths.

## Risks And Test Signals

Risks include callers mixing managed and unmanaged removal for the same controller, or assuming `devm_spmi_controller_add()` owns the allocation when it only registers a removal action. Test signals are probe-failure unwinds before and after controller add, driver unbind, module unload, repeated bind/unbind under KASAN/KMEMLEAK, and checking that controller children disappear before the allocation reference is released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-mtk-pmif.c -->
# sources/distributed-fs/ceph-client/drivers/spmi/spmi-mtk-pmif.c

## Purpose

`spmi-mtk-pmif.c` implements MediaTek's PMIF-backed SPMI controller driver for MT6873, MT8195, and MT8196-style SoCs. It maps SoC-specific PMIF and SPMI master register layouts, issues SPMI read/write/reset/sleep/shutdown/wakeup commands through a software-interface channel, manages clocks, and for SPMI v2 hardware exposes an IRQ domain for remote-control/status interrupts by slave ID.

## Important APIs, Types, And Functions

Important types are `struct ch_reg` for selected software-interface channel register indexes, `struct pmif_data` for SoC register tables and capabilities, `struct pmif_bus` for each SPMI bus instance, and `struct pmif` for the parent device's shared state. SoC data tables include `mt6873_regs`, `mt8195_regs`, `mt6873_spmi_regs`, `mt8195_spmi_regs`, `mt6873_pmif_arb`, `mt8195_pmif_arb`, and `mt8196_pmif_arb`.

Register helpers are `pmif_readl()`, `pmif_writel()`, `mtk_spmi_readl()`, `mtk_spmi_writel()`, and `pmif_is_fsm_vldclr()`. SPMI callbacks are `pmif_arb_cmd()`, `pmif_spmi_read_cmd()`, and `pmif_spmi_write_cmd()`. IRQ support is implemented by `mtk_spmi_handle_chained_irq()`, `mtk_spmi_rcs_irq_eoi()`, `mtk_spmi_rcs_irq_enable()`, `mtk_spmi_rcs_irq_disable()`, `mtk_spmi_rcs_irq_set_wake()`, `mtk_spmi_rcs_irq_translate()`, `mtk_spmi_rcs_irq_alloc()`, `mtk_spmi_irq_init()`, and `mtk_spmi_irq_remove()`. Probe/remove paths are `mtk_spmi_bus_probe()`, `mtk_spmi_probe()`, and `mtk_spmi_remove()`.

## Control Flow And State

Parent probe allocates `struct pmif`, selects SoC match data, stores it as platform driver data, then either probes one bus from the parent node or iterates child nodes named `spmi` when the SoC supports multiple SPMI buses. After bus probing, it computes the selected software-interface channel from `soc_chan` and stores register indexes for status, write data, read data, command send, and valid-clear.

Each bus probe determines a bus ID from OF aliases for multi-bus SoCs, allocates an SPMI controller, maps `pmif` and `spmimst` register resources by name, obtains and enables the three clocks, initializes SPMI v2 IRQ support when applicable, installs SPMI command/read/write callbacks, assigns the controller OF node and name, initializes the raw spinlock, adds the controller, and finally attaches a chained IRQ handler if an IRQ domain exists. Remove walks all bus slots, removes IRQ domains and chained handlers, removes SPMI controllers, disables clocks, and releases clock references.

Reads validate SID and length, map framework opcodes into PMIF command classes, wait for the software-interface FSM to become idle, issue a packed command, wait for `SWINF_WFVLDCLR`, read a 32-bit data register, clear the valid flag, unlock, and copy the requested bytes to the caller. Writes validate SID/length/opcode class, copy bytes into a 32-bit word, wait for idle, write the data register, issue a packed write command, and return after command submission. Both paths serialize the shared software interface with `raw_spin_lock_irqsave()`.

SPMI command opcodes for reset/sleep/shutdown/wakeup use the SPMI master operation-state registers and poll `SPMI_OP_ST_STA`. SPMI v2 IRQ handling creates an IRQ domain, clears stale bootloader interrupts, translates firmware interrupt specs by SID, tracks min/max SIDs seen, handles the parent chained IRQ by scanning only relevant SPMI interrupt banks, dispatches one domain IRQ per enabled SID, and acknowledges by writing the eight-bit bank mask back to the hardware register.

## State And Persistence Behavior

Persistent runtime state includes SoC register mapping tables, MMIO bases, enabled clocks, per-bus IRQ domain, enabled-SID bitmap, min/max SIDs discovered by IRQ translation, and the selected software-interface channel register indexes. No disk state is involved. Hardware interrupt flags are cleared during IRQ init and on child IRQ EOI; clock state persists while the platform device is bound.

## Dependencies And Integration Points

The driver depends on OF match data and aliases, named MMIO resources, named clocks (`pmif_sys_ck`, `pmif_tmr_ck`, `spmimst_clk_mux`), the SPMI framework, IRQ domains, chained IRQ handling, raw spinlocks, and atomic MMIO polling. It integrates with PMIC child devices through the SPMI bus and, for v2, with device-tree interrupt consumers through the controller's IRQ domain.

## Risks And Test Signals

Risks include mismatched register tables for SoC variants, incorrect software-interface channel selection, raw-spinlocked polling under long hardware stalls, no explicit zero-length rejection before `(len - 1)` encoding, write command completion not being polled after submission, IRQ-bank decoding that depends on SID-to-bank math, and multi-bus overflow if firmware exposes more child buses than `PMIF_MAX_BUSES`. The `pmif_arb_cmd()` poll condition appears to wait for the busy bit to become set rather than clear, which deserves hardware confirmation.

Useful tests include probe/remove for each compatible, missing clock/resource/alias failures, 1-4 byte read/write transfers, invalid SID/opcode/length handling, PMIF FSM timeout with valid-clear recovery, reset/sleep/shutdown/wakeup commands, multi-bus MT8196 enumeration, SPMI v2 IRQ domain allocation from firmware specs, wake enable propagation, stale interrupt clearing, chained IRQ dispatch only for enabled SIDs, and repeated bind/unbind checking clocks and controller removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-mtk-pmif.c -->
