# Research: subset-b-003815

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/ssi_protocol.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/clients/ssi_protocol.c

## Purpose
Implements the SSI McSAAB protocol as an HSI client driver and exposes it as a Phonet point-to-point net_device named `phonet%d`. It translates Phonet sk_buffs into HSI data-channel messages, drives a command-channel handshake with the modem/CMT, and provides exported helpers for sibling HSI slave clients that need to coordinate use of the shared SSI wake line.

## Important APIs, Types, and Functions
- `struct ssi_protocol` is the main per-client state object. It tracks `main_state`, `send_state`, `recv_state`, TX/RX message IDs, watchdog timers, keep-alive timer, command/data HSI channel IDs, command pool, TX queue, and Phonet netdev.
- Exported helpers: `ssip_slave_get_master()`, `ssip_slave_start_tx()`, `ssip_slave_stop_tx()`, `ssip_slave_running()`, and `ssip_reset_event()`.
- Netdev operations: `ssip_pn_open()`, `ssip_pn_stop()`, `ssip_pn_xmit()`.
- HSI callbacks: `ssip_rxcmd_complete()`, `ssip_rx_data_complete()`, `ssip_tx_data_complete()`, `ssip_swbreak_complete()`, and `ssip_port_event()`.

## Control Flow
Probe allocates `struct ssi_protocol`, resolves `mcsaab-control` and `mcsaab-data` channel IDs, preallocates command messages, registers a Phonet netdev, and links the instance on `ssip_list`. Opening the netdev claims the HSI port shared, registers wake-line event handling, configures the port, starts a wake test, enters `HANDSHAKE`, sends `BOOTINFO_REQ`, and posts a command read. Command completions re-arm the command read before dispatching command IDs. Handshake moves through boot-info request/response and `WAKETEST_RESULT`; a successful wake test marks `ACTIVE`, enables carrier, and wakes the TX queue. TX queues Phonet packets as HSI data messages, raises wake with `hsi_start_tx()`, waits for `READY`, sends `START_TRANS`, writes data, then sends `SWBREAK` before returning to idle or ready. RX wake events send `READY`; `START_TRANS` allocates an skb and reads the data payload, then injects it into the Phonet stack.

## State and Persistence
State is in memory only: lists, timers, atomics, message IDs, and carrier state. There is no persistent storage. `ssip_reset()` flushes HSI transfers, stops wake usage, cancels timers/work, clears state, and frees queued TX messages. Command messages are pooled and recycled through destructors.

## Dependencies and Integration Points
Depends on the HSI core API (`hsi_claim_port`, `hsi_async_read/write`, `hsi_start_tx`, `hsi_stop_tx`, events), OMAP SSI's exported `ssi_waketest()` workaround, Linux netdev/Phonet APIs, sk_buff scatter-gather helpers, timers, workqueues, and spinlocks.

## Risks and Test Signals
Key risks are async completion ordering, watchdog reset during callbacks, command-pool exhaustion if destructors are bypassed, wake-line reference imbalance through slave helper users, and assumptions about host/modem endianness. Test signals include Phonet netdev registration, successful boot/wake-test transition to carrier on, TX queue stop/wake behavior near `SSIP_TXQUEUE_LEN`, watchdog-triggered reset recovery, RX/TX ID mismatch handling, and module unload after active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/ssi_protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hsi/controllers/Kconfig

## Purpose
Defines the HSI controller submenu and the `OMAP_SSI` build option for the legacy OMAP Synchronous Serial Interface hardware driver.

## Important APIs, Types, and Functions
This is Kconfig metadata rather than C code. `config OMAP_SSI` is a tristate option titled "OMAP SSI hardware driver".

## Control Flow
The option is visible under the HSI controllers comment. It can be built in, modular, or disabled when its dependencies are satisfied.

## State and Persistence
No runtime state. The selected Kconfig value persists in the kernel build configuration and controls whether `omap_ssi.o` is built.

## Dependencies and Integration Points
Requires `HSI`, `OF`, `COMMON_CLK`, and either `ARCH_OMAP3` or `COMPILE_TEST`. It integrates with the local controller Makefile, which maps `CONFIG_OMAP_SSI` to the OMAP SSI object.

## Risks and Test Signals
Risk is mostly dependency coverage: the driver assumes device-tree data, common clock support, and OMAP-compatible resources. Build testing should cover both `ARCH_OMAP3` and `COMPILE_TEST`, including module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hsi/controllers/Makefile

## Purpose
Builds the OMAP SSI controller module from its controller-level and port-level implementation files.

## Important APIs, Types, and Functions
The Makefile defines `omap_ssi-objs += omap_ssi_core.o omap_ssi_port.o` and attaches the composed object to `obj-$(CONFIG_OMAP_SSI)`.

## Control Flow
Kbuild includes both implementation files in one module/object when `CONFIG_OMAP_SSI` is enabled. This lets `omap_ssi_core.c` register both the controller platform driver and the externally declared `ssi_port_pdriver` from `omap_ssi_port.c`.

## State and Persistence
No runtime state. Build state is controlled by Kconfig and Kbuild.

## Dependencies and Integration Points
Integrates with `drivers/hsi/controllers/Kconfig` and the Linux Kbuild object aggregation model. The split object layout matches shared declarations in `omap_ssi.h`.

## Risks and Test Signals
Risk is link-time coupling between the two objects; missing either object breaks `ssi_port_pdriver` or controller callbacks. Test signals are successful `CONFIG_OMAP_SSI=m` and `=y` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi.h -->
# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi.h

## Purpose
Provides the private shared interface between OMAP SSI controller and port code.

## Important APIs, Types, and Functions
- Constants: `SSI_MAX_CHANNELS`, `SSI_MAX_GDD_LCH`, `SSI_BYTES_TO_FRAMES()`, and `SSI_WAKE_EN`.
- `struct omap_ssm_ctx` stores shadow context for SST/SSR mode, channels, frame size, timeout, arbitration, and divisor.
- `struct omap_ssi_port` owns per-port MMIO bases, DMA addresses, wake GPIO/IRQ, locks, transfer queues, error work, runtime context, and debugfs entry.
- `struct gdd_trn` binds a GDD logical channel to an active `hsi_msg` and scatterlist.
- `struct omap_ssi_controller` owns controller MMIO, clock, GDD IRQ/tasklet state, GDD transaction table, notifier, max speed, saved GDD context, and port array.
- Declares `omap_ssi_port_update_fclk()` and `ssi_port_pdriver`.

## Control Flow
This header has no executable flow, but its structures define how `omap_ssi_core.c` and `omap_ssi_port.c` coordinate GDD completions, port probing, runtime PM context restore, and clock-rate changes.

## State and Persistence
All state is volatile driver-private state. Shadow fields are used to restore hardware registers after runtime suspend or context loss; they are not persisted across driver unload.

## Dependencies and Integration Points
Depends on Linux device, platform, HSI, GPIO descriptor, IRQ, IO, module, and DMA types. It is tightly coupled to `omap_ssi_regs.h` register definitions and the HSI framework structs.

## Risks and Test Signals
Risks include mismatched assumptions about channel count, GDD logical channel ownership, and wake reference state. Test signals include runtime suspend/resume preserving SST/SSR configuration, GDD DMA completion freeing logical channels, and debugfs compiling under `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_core.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_core.c

## Purpose
Implements the OMAP SSI controller platform driver, controller registration with the HSI bus, GDD DMA completion handling, controller-level runtime PM, debugfs, and clock-rate change coordination.

## Important APIs, Types, and Functions
- Platform driver `ssi_pdriver` for `ti,omap3-ssi`.
- Module init/exit register both `ssi_pdriver` and `ssi_port_pdriver`.
- `ssi_add_controller()`, `ssi_hw_init()`, `ssi_remove_controller()`, and `ssi_probe()` build the HSI controller.
- `ssi_gdd_isr()`, `ssi_gdd_tasklet()`, and `ssi_gdd_complete()` handle GDD interrupts and complete DMA-backed HSI messages.
- `ssi_clk_event()` pauses ports during functional clock changes and calls `omap_ssi_port_update_fclk()`.
- Exported `ssi_waketest()` drives a legacy wake-line test workaround used by SSI protocol.

## Control Flow
Probe counts available `ti,omap3-ssi-port` child nodes, allocates an HSI controller, maps `sys` and `gdd` resources, requests the GDD IRQ, gets the functional clock, registers a clock notifier, registers the HSI controller, enables runtime PM, resets/configures GDD, creates debugfs, and creates child platform devices for ports. GDD IRQ disables itself and schedules a high-priority tasklet. The tasklet reads pending logical channel bits, calls `ssi_gdd_complete()`, acknowledges status, and either reschedules or re-enables the IRQ. Completion unmaps DMA, releases the GDD logical channel, marks status/error, moves timeout failures to the port error queue, and re-arms the per-port PIO interrupt needed to finish the logical transfer.

## State and Persistence
Uses IDA-assigned controller IDs, saved `gdd_gcr`, cached clock rate in kHz, `max_speed`, and optional context loss counter. Runtime suspend captures context-loss state; resume restores GDD control if needed. State is volatile and reinitialized on probe.

## Dependencies and Integration Points
Integrates HSI core allocation/registration, OF platform children, common clock notifiers, pm_runtime, IRQ/tasklets, DMA mapping, debugfs, and OMAP SSI registers. It coordinates with port code through `struct omap_ssi_controller` and `omap_ssi_port_update_fclk()`.

## Risks and Test Signals
Risks include IRQ/tasklet races on teardown, clock notifier disabling invalid wake IRQs, runtime PM imbalance on GDD error paths, and context restore gaps because `get_loss` is currently NULL. Test signals include probing with multiple ports, GDD DMA timeout recovery, clock-rate transition under traffic, runtime suspend/resume, debugfs register reads, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_port.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_port.c

## Purpose
Implements the per-port OMAP SSI HSI controller operations: async transfer queuing, PIO and GDD-DMA transfer setup, wake-line handling, HSI port setup/flush/release, per-port IRQs, runtime PM context save/restore, and port debugfs.

## Important APIs, Types, and Functions
- HSI port callbacks assigned in probe: `ssi_async()`, `ssi_setup()`, `ssi_flush()`, `ssi_start_tx()`, `ssi_stop_tx()`, and `ssi_release()`.
- Transfer helpers: `ssi_start_transfer()`, `ssi_start_dma()`, `ssi_start_pio()`, `ssi_pio_complete()`, and `ssi_transfer()`.
- Interrupt threads: `ssi_pio_thread()` for data/error/break interrupts and `ssi_wake_thread()` for CAWAKE changes.
- Cleanup helpers: `ssi_cleanup_gdd()`, `ssi_cleanup_queues()`, `ssi_flush_queue()`, and `ssi_process_errqueue()`.
- Runtime PM helpers save/restore SST/SSR and MPU interrupt context.

## Control Flow
Port probe picks the first uninitialized port slot from the parent controller, obtains the CAWAKE GPIO, allocates port private data, maps TX/RX MMIO, requests the data IRQ and wake IRQ, initializes queues/locks/work, enables autosuspend runtime PM, creates debugfs, and registers DT-described HSI clients. Async transfers are queued per TX/RX channel. Single-word transfers use PIO interrupt bits; larger single-entry scatterlists claim a GDD logical channel and program DMA registers. PIO IRQ loops through enabled pending status, completing TX/RX frames, break events, and error handling. Wake IRQ toggles runtime PM references and notifies HSI clients with start/stop RX events. Release and flush cancel DMA, clear buffers/status, drain queues, and reset port mode when the last client exits.

## State and Persistence
Per-port state includes queue contents, wake refcount, wake-in flag, SST/SSR shadow context, active GDD linkage through the controller, error queue work, and debugfs state. Runtime suspend writes modules to sleep and saves registers; resume restores divisor, mode, and context when needed. No persistent storage.

## Dependencies and Integration Points
Depends on the HSI framework, parent OMAP SSI controller data, GDD registers, pm_runtime, GPIO descriptors, pinctrl sleep/default states, IRQ threading, DMA mapping, scatterlists, debugfs, and DT child client registration.

## Risks and Test Signals
Risks include PM reference imbalance between PIO, DMA, wake, and flush paths; list manipulation during callbacks; partial scatter-gather support (`nents > 1` returns `-ENOSYS`); BUG_ON on invalid channels; and teardown races with IRQ/work. Test signals include PIO and DMA transfer completion, break receive/send in frame mode, error IRQ recovery, wake transitions with rapid high-low-high changes, flush during active DMA, autosuspend/resume preserving register state, and DT child client creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_regs.h

## Purpose
Defines OMAP SSI hardware register offsets and bit fields for SYS, SST, SSR, and GDD blocks.

## Important APIs, Types, and Functions
This is a register-definition header. It provides macros such as `SSI_MPU_STATUS_REG(port, irq)`, `SSI_MPU_ENABLE_REG(port, irq)`, `SSI_WAKE_REG(port)`, `SSI_SST_BUFFER_CH_REG(channel)`, `SSI_SSR_BUFFER_CH_REG(channel)`, and GDD channel register macros.

## Control Flow
No executable control flow. The macros are consumed by controller and port code for MMIO reads/writes, interrupt masking/acknowledgement, DMA programming, wake manipulation, and context restore.

## State and Persistence
The file itself has no state. It names hardware state held in SSI registers: wake bits, interrupt enable/status, SST/SSR modes and buffers, SSR errors, GDD logical channel descriptors, and GDD global control.

## Dependencies and Integration Points
Integrated with `omap_ssi_core.c`, `omap_ssi_port.c`, and `omap_ssi.h`. The values encode the contract with OMAP SSI hardware and the GDD DMA engine.

## Risks and Test Signals
Risks are incorrect offsets, bit masks, or channel calculations causing silent hardware corruption. Test signals include successful register debugfs dumps, correct interrupt ack/mask behavior, DMA descriptor operation on all logical channels, and wake bit manipulation on each port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/hsi_boardinfo.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/hsi_boardinfo.c

## Purpose
Provides the board-file registration path for statically described HSI clients.

## Important APIs, Types, and Functions
- Global `hsi_board_list` stores `struct hsi_cl_info` entries and is exported GPL for internal framework use.
- `hsi_register_board_info()` copies an array of `struct hsi_board_info` into allocated list entries during init.

## Control Flow
Callers pass board info and length. The function allocates an array of `struct hsi_cl_info`, copies each board entry, and appends it to `hsi_board_list`. Later, `hsi_core.c` scans the list when a matching controller registers and instantiates clients on the requested port.

## State and Persistence
The global list persists for the life of the kernel. Entries are allocated during init and are not freed here, matching traditional board-info registration patterns.

## Dependencies and Integration Points
Depends on `hsi_core.h`, list APIs, slab allocation, and the HSI framework's `struct hsi_board_info`. It integrates with `hsi_scan_board_info()` in `hsi_core.c`.

## Risks and Test Signals
Risks include allocation failure, stale board data, or mismatched HSI controller/port IDs causing clients not to appear. Test signals include static board clients being created after controller registration and graceful `-ENOMEM` on allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/hsi_boardinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.c

## Purpose
Implements the Linux HSI bus core: bus registration/matching, controller and port allocation/registration, client creation from board info or device tree, message allocation/freeing, async dispatch, port claim/release, event notifier plumbing, and channel-name lookup.

## Important APIs, Types, and Functions
- Bus type `hsi_bus_type` with modalias, uevent, OF/name matching, and device attributes.
- Client/controller APIs: `hsi_new_client()`, `hsi_register_controller()`, `hsi_unregister_controller()`, `hsi_register_client_driver()`, `hsi_alloc_controller()`, `hsi_put_controller()`.
- Message APIs: `hsi_alloc_msg()`, `hsi_free_msg()`, `hsi_async()`.
- Port APIs: `hsi_claim_port()`, `hsi_release_port()`, `hsi_register_port_event()`, `hsi_unregister_port_event()`, `hsi_event()`, `hsi_get_channel_id_by_name()`.
- OF helper `hsi_add_clients_from_dt()` registers `hsi_char` and child client nodes.

## Control Flow
Postcore init registers the HSI bus. Controller drivers allocate controllers with initialized ports and dummy callbacks, then register them. Registration adds controller and port devices and scans static board info. DT port code can add clients by parsing mode, speed, flow, arbitration, and channel IDs/names. Clients must claim a port before async transfers; `hsi_async()` verifies the claim and delegates to the controller port callback. Event registration attaches a client notifier to a port blocking notifier chain.

## State and Persistence
Controller, port, and client objects are kernel devices with release callbacks. Port state includes claim count, sharing flag, mutex, and notifier chain. Client TX/RX channel arrays are duplicated and freed on device release. No disk persistence.

## Dependencies and Integration Points
Uses Linux driver core, OF helpers, notifier chains, scatterlists through HSI messages, module reference counting, and static board info from `hsi_boardinfo.c`. Controller drivers supply actual port operations.

## Risks and Test Signals
Risks include shared-port claim semantics, module reference imbalance on release, async callbacks occurring before `hsi_async()` returns, malformed DT properties, and null channel names in lookup. Test signals include bus modalias autoloading, DT client enumeration, static board client enumeration, shared/exclusive claim behavior, event callbacks in interrupt context, and cleanup order on unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.h -->
# sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.h

## Purpose
Defines private HSI core structures shared by board-info registration and core bus scanning.

## Important APIs, Types, and Functions
- `struct hsi_cl_info` wraps `struct hsi_board_info` with a list node.
- Declares the global `hsi_board_list`.

## Control Flow
No executable control flow. `hsi_boardinfo.c` appends entries to `hsi_board_list`; `hsi_core.c` scans it when controllers are registered.

## State and Persistence
The header describes the in-memory static-client registry. Persistence is kernel-lifetime only.

## Dependencies and Integration Points
Depends on public `<linux/hsi/hsi.h>` for `struct hsi_board_info` and list infrastructure through included kernel headers.

## Risks and Test Signals
Risks are limited to structure coupling between the two C files. Test signals are successful static client registration and no duplicate external definition of `hsi_board_list`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hte/Kconfig

## Purpose
Defines build options for the Hardware Timestamping Engine subsystem, the Tegra194-compatible provider, and the Tegra HTE test driver.

## Important APIs, Types, and Functions
Kconfig options are `HTE`, `HTE_TEGRA194`, and `HTE_TEGRA194_TEST`.

## Control Flow
`menuconfig HTE` gates the subsystem. When enabled, users can select the NVIDIA Tegra provider and optional test driver.

## State and Persistence
No runtime state. The selected configuration persists in the kernel `.config` and controls object inclusion.

## Dependencies and Integration Points
`HTE_TEGRA194` depends on Tegra architecture or compile testing plus `GPIOLIB`. The test driver depends on `HTE_TEGRA194` or compile testing.

## Risks and Test Signals
Risks include compiling the test driver without matching hardware or provider support. Test signals include `CONFIG_HTE=y/m`, provider module builds, and compile-test coverage outside Tegra.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hte/Makefile

## Purpose
Maps HTE Kconfig symbols to their build outputs.

## Important APIs, Types, and Functions
Builds `hte.o` for `CONFIG_HTE`, `hte-tegra194.o` for `CONFIG_HTE_TEGRA194`, and `hte-tegra194-test.o` for `CONFIG_HTE_TEGRA194_TEST`.

## Control Flow
Kbuild includes objects conditionally based on configuration. The core must be present for providers and consumers to link against exported HTE APIs.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with `drivers/hte/Kconfig` and standard kernel module/built-in build flows.

## Risks and Test Signals
Risk is missing dependency coverage if provider/test are selected without core symbols. Test signals are successful allmodconfig/allyesconfig and targeted HTE module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/hte-tegra194-test.c -->
# sources/distributed-fs/ceph-client/drivers/hte/hte-tegra194-test.c

## Purpose
Demonstrates and tests HTE consumer APIs on Tegra by timestamping a GPIO input and a LIC IRQ line, while periodically toggling a GPIO output to create timestampable events.

## Important APIs, Types, and Functions
- Global test state `struct tegra_hte_test hte` stores GPIOs, IRQ, descriptors, timer, and device pointer.
- `process_hw_ts()` is the HTE callback that logs timestamp, sequence, line ID, and edge.
- `tegra_hte_test_probe()` acquires GPIOs/IRQ, counts DT timestamp requests, initializes descriptors, calls `hte_ts_get()`, and requests timestamps with `devm_hte_request_ts_ns()`.
- `gpio_timer_cb()` toggles the output every 8 seconds after initial start.

## Control Flow
Probe gets output and input GPIOs, sets directions, maps input GPIO to an IRQ, registers a minimal rising-edge IRQ handler, queries `of_hte_req_count()`, allocates descriptors, initializes each descriptor, binds each through `hte_ts_get()`, and requests HTE callbacks. It then starts a timer that toggles the output pin. Remove frees IRQ/GPIO resources and deletes the timer.

## State and Persistence
State is a single global test instance, so only one active device is represented. Timestamp descriptor lifetime is mostly devm-managed after request; explicit `hte_ts_put()` is used only for failures before managed request succeeds. No persistent storage.

## Dependencies and Integration Points
Depends on GPIO descriptor APIs, IRQ APIs, OF timestamp properties, HTE consumer APIs, timers, and platform-driver matching on `nvidia,tegra194-hte-test`.

## Risks and Test Signals
Risks include global singleton state, manual GPIO/IRQ cleanup mixed with devm HTE cleanup, probe error paths around `request_irq()`, and requiring physical GPIO loopback. Test signals are logged `HW timestamp(...)` lines for GPIO toggles and LIC activity, clean unload, and failure behavior when DT timestamp entries are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/hte-tegra194-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/hte-tegra194.c -->
# sources/distributed-fs/ceph-client/drivers/hte/hte-tegra194.c

## Purpose
Implements the NVIDIA Tegra Generic/Hardware Timestamping Engine provider for AON GPIO and LIC interrupt sources across Tegra194, Tegra234, and Tegra264 variants.

## Important APIs, Types, and Functions
- SoC data: `struct tegra_hte_data` captures provider type, slice count, mapping tables, and timestamp clock rate.
- Runtime state: `struct tegra_hte_soc`, `struct hte_slices`, and `struct tegra_hte_line_data`.
- HTE provider ops: `tegra_hte_request()`, `tegra_hte_release()`, `tegra_hte_enable()`, `tegra_hte_disable()`, and `tegra_hte_clk_src_info()`.
- Translation: `tegra_hte_line_xlate()`, `tegra_hte_line_xlate_plat()`, and `tegra_hte_match_from_linedata()`.
- IRQ/FIFO path: `tegra_hte_isr()` and `tegra_hte_read_fifo()`.

## Control Flow
Probe selects SoC data from OF, reads optional slice and interrupt-threshold properties, maps registers, requests the provider IRQ, fills an `hte_chip`, resolves GPIO controller linkage for GPIO providers, registers with the HTE core, initializes slice locks, and enables the hardware with interrupt threshold. Consumers request lines through HTE core translation. GPIO requests enable hardware timestamping on the GPIO descriptor and then set the corresponding slice enable bit. On IRQ, the driver drains FIFO entries, reconstructs the timestamp counter, reads source slice and previous/current vectors, computes changed bits, converts each bit to a line ID, fills `hte_ts_data`, and calls `hte_push_ts_ns()`.

## State and Persistence
State includes mapped registers, slice enable shadow values for suspend, suspend flags per slice, GPIO line data, threshold, and clock-rate metadata. Suspend saves control and slice enable registers and marks slices suspended; resume restores control and enables. No persistent storage.

## Dependencies and Integration Points
Depends on HTE provider APIs, GPIO descriptor/device APIs, platform resources, OF compatible data, IRQ handling, MMIO, and Tegra-specific line maps. GPIO consumers can bind by DT phandle or platform line data.

## Risks and Test Signals
Risks include off-by-one bounds checks (`> nlines` versus `>= nlines` patterns), invalid GPIO map entries, FIFO drain under heavy event rates, suspend blocking enable/disable, GPIO controller lookup differences for Tegra194 versus later SoCs, and raw-level reads racing line release. Test signals include successful provider registration for each compatible, timestamp callbacks from GPIO and LIC sources, clock source info correctness, suspend/resume preserving enabled lines, and dropped timestamp counters remaining low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/hte-tegra194.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/hte.c -->
# sources/distributed-fs/ceph-client/drivers/hte/hte.c

## Purpose
Implements the generic Hardware Timestamping Engine core that connects provider chips with consumers requesting timestamped lines.

## Important APIs, Types, and Functions
- Core state: global `hte_devices` protected by `hte_lock`; per-provider `struct hte_device`; per-line `struct hte_ts_info`.
- Consumer APIs: `of_hte_req_count()`, `hte_init_line_attr()`, `hte_ts_get()`, `hte_request_ts_ns()`, `devm_hte_request_ts_ns()`, `hte_enable_ts()`, `hte_disable_ts()`, `hte_ts_put()`, and `hte_get_clk_src_info()`.
- Provider APIs: `devm_hte_register_chip()` and `hte_push_ts_ns()`.

## Control Flow
Providers register an `hte_chip`; the core allocates a flex-array `hte_device`, initializes one `hte_ts_info` per line, links it globally, and creates debugfs. Consumers initialize attributes, then `hte_ts_get()` finds a provider either through DT phandles or provider `match_from_linedata`, calls provider translation, module-pins the provider, and binds the descriptor to a free line. `hte_request_ts_ns()` calls provider request, stores callbacks, initializes optional work for sleeping callbacks, creates per-line debugfs, and marks the line registered. Providers push timestamp data with `hte_push_ts_ns()`, which sequences events, drops unregistered/disabled pushes, calls the primary callback under spinlock, and queues the secondary callback when requested. Release disables provider state, flushes queued work, clears flags, removes debugfs, and module_puts.

## State and Persistence
State is in memory: per-line flags (`REQ`, `REGISTERED`, `DISABLE`, `QUEUE_WK`), sequence counters, callback pointers, client data, line names, dropped timestamp counts, locks, and debugfs dentries. There is no persistent storage.

## Dependencies and Integration Points
Integrates with OF phandle parsing, module reference counts, debugfs, workqueues, mutexes/spinlocks, provider `hte_ops`, and public `<linux/hte.h>` descriptors.

## Risks and Test Signals
Risks include callback invocation under spinlock, release racing queued secondary work, provider unregister while descriptors are live, line-name ownership (`free_attr_name`), and duplicate requests for one line. Test signals include duplicate request returning `-EUSERS`, disable dropping timestamps, secondary callback work flushing on release, devm release on consumer remove, provider unregister cleanup, and debugfs counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hte/hte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hv/Kconfig

## Purpose
Defines build configuration for Microsoft Hyper-V guest and root/VTL support drivers.

## Important APIs, Types, and Functions
Kconfig options include `HYPERV`, `HYPERV_VTL_MODE`, `HYPERV_TIMER`, `HYPERV_UTILS`, `HYPERV_BALLOON`, `HYPERV_VMBUS`, `MSHV_ROOT`, and `MSHV_VTL`.

## Control Flow
The menu exposes core hypervisor support first, then dependent drivers. `HYPERV_VMBUS` defaults to `HYPERV`; utilities, balloon, root partition, and VTL drivers depend on core VMBus or VTL-mode capabilities.

## State and Persistence
No runtime state. The selected `.config` controls which Hyper-V objects are built and whether core support is built in.

## Dependencies and Integration Points
Depends on architecture/hypervisor symbols, paravirt, local APIC or ARM64 constraints, connector/NLS/PTP for utilities, page reporting for ballooning, and memory-management features for root/VTL drivers.

## Risks and Test Signals
Risks include invalid architecture combinations, VTL-mode assumptions, and page-size constraints for root partition support. Test signals include build coverage for x86_64 and ARM64, VMBus built-in default behavior, and dependency resolution for utility/balloon/root/VTL modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hv/Makefile

## Purpose
Maps Hyper-V Kconfig options to composed kernel objects and module build units.

## Important APIs, Types, and Functions
Defines `hv_vmbus-y` from `vmbus_drv.o`, `hv.o`, `connection.o`, `channel.o`, `channel_mgmt.o`, `ring_buffer.o`, and `hv_trace.o`; plus composed objects for utilities, root partition support, and VTL support.

## Control Flow
Kbuild links component objects into modules/built-ins based on configuration. `hv_common.o` is built when `CONFIG_HYPERV` is enabled, and `hv_proc.o`/`mshv_common.o` are conditionally built for MSHV support.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with `drivers/hv/Kconfig`, trace include paths via `CFLAGS_hv_trace.o`, and optional debugfs/tracepoint objects.

## Risks and Test Signals
Risks include missing object membership for exported symbols, incorrect built-in/module split for shared common code, and optional feature link failures. Test signals are successful builds for VMBus-only, utilities, balloon, MSHV root, MSHV VTL, debugfs, and tracepoint configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/channel.c -->
# sources/distributed-fs/ceph-client/drivers/hv/channel.c

## Purpose
Implements core VMBus channel operations for Hyper-V guests: event notification, ring allocation/freeing, GPADL establishment/teardown, channel open/close/reconnect, packet send/receive, channel retargeting, and request ID tracking.

## Important APIs, Types, and Functions
- Ring APIs: `vmbus_alloc_ring()`, `vmbus_free_ring()`, `vmbus_open()`, `vmbus_connect_ring()`, `vmbus_close()`, `vmbus_disconnect_ring()`.
- GPADL APIs: `vmbus_establish_gpadl()`, internal `__vmbus_establish_gpadl()`, `create_gpadl_header()`, and `vmbus_teardown_gpadl()`.
- Packet APIs: `vmbus_sendpacket_getid()`, `vmbus_sendpacket()`, `vmbus_sendpacket_mpb_desc()`, `vmbus_recvpacket()`, and `vmbus_recvpacket_raw()`.
- Requestor APIs: `vmbus_next_request_id()`, `vmbus_request_addr_match()`, `__vmbus_request_addr_match()`, and `vmbus_request_addr()`.
- Retargeting and notification: `vmbus_setevent()`, `vmbus_send_modifychannel()`.

## Control Flow
Opening a channel allocates or reuses ring pages, optionally initializes the requestor array, establishes a ring GPADL with the host, initializes outbound and inbound ring buffers, posts `CHANNELMSG_OPENCHANNEL`, waits for completion, and transitions state to opened. GPADL establishment builds header/body channel messages for Hyper-V page PFNs, may decrypt memory for host visibility, posts messages, waits for creation status, and records the handle. Close resets callbacks/tasklet access, posts `CHANNELMSG_CLOSECHANNEL`, tears down the ring GPADL, frees requestor state, and then frees ring pages. Packet send builds aligned VMBus descriptors and writes kvecs into the ring; receive delegates to ring-buffer read. Modify-channel uses ACK waiting only for VMBus protocol 5.3 and newer.

## State and Persistence
Per-channel state includes open state, ring page pointer/count/send offset, GPADL handle/buffer/size/decrypted flag, callbacks, requestor freelist/bitmap, target CPU, rescind flag, and close message storage. State is volatile; no disk persistence. Confidential-computing memory visibility is tracked so failed re-encryption intentionally leaks memory rather than freeing pages in an unknown encryption state.

## Dependencies and Integration Points
Depends on VMBus connection globals, Hyper-V message protocols, ring-buffer implementation, architecture Hyper-V page/PFN helpers, tasklets, completions, spinlocks, mutexes, memory encryption helpers, tracing, and exported symbols used by Hyper-V service drivers such as netvsc/storvsc/utilities.

## Risks and Test Signals
Risks include GPADL PFN math for PAGE_SIZE versus HV_HYP_PAGE_SIZE, memory encryption/decryption failure handling, rescind races while waiting for host completions, callback/tasklet races during close, requestor ID exhaustion or leaks, and version-specific modify-channel ACK behavior. Test signals include open/close under rescind, channel retargeting on old/new protocol versions, packet send/receive alignment, GPADL teardown re-encryption, ring reconnect, requestor allocation/match/free cycles, and service driver unload while callbacks are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/channel.c -->
