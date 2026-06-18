# Research: subset-b-004280

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sunplus-mmc.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sunplus-mmc.c

Purpose: this is the Sunplus SP7021 MMC/SD host controller driver. It implements a non-SDHCI MMC host around Sunplus command, status, timing, DMA-sector, and PIO registers, providing card requests, bus clock/timing/width setup, software reset, runtime PM clock gating, and simple tuning.

Important APIs, types, and functions: `struct spmmc_host` holds the MMIO base, clock, reset, current `mmc_request`, DMA/PIO mode, threaded IRQ state, and `struct spmmc_tuning_info`. The MMC entry points are `spmmc_request()`, `spmmc_set_ios()`, `spmmc_get_cd()`, and `spmmc_execute_tuning()`. Core helpers include `spmmc_prepare_cmd()`, `spmmc_prepare_data()`, `spmmc_finish_request()`, `spmmc_check_error()`, `spmmc_xfer_data_pio()`, `spmmc_sw_reset()`, and `spmmc_controller_init()`.

Control flow: probe allocates an MMC host, maps registers, gets the clock and reset, requests a threaded IRQ, enables the clock, parses DT/MMC properties, obtains regulators, sets request and segment limits, initializes the controller, enables tuning, starts runtime PM, and registers with `mmc_add_host()`. A request programs command bytes and response mode; R2 commands are handled synchronously, PIO data is polled through the FIFO, small DMA requests are also waited synchronously, and large DMA requests complete from the threaded interrupt. Completion unmaps DMA, reads the response buffers, checks controller status/error bits, optionally sends STOP, clears `host->mrq`, and calls `mmc_request_done()`.

State and persistence: persistent software state is limited to the current request, DMA interrupt threshold/use flag, DMA-vs-PIO mode, and adaptive tuning delay fields. Hardware state includes selected SD media mode, clock divider, timing delays, data width, DMA sector descriptors, interrupt enables, and reset state. Runtime suspend/resume only disables or reenables the module clock.

Dependencies and integration points: the driver uses the MMC core, DT parsing, regulator helpers, common clock/reset APIs, DMA mapping, threaded IRQs, `readl_poll_timeout()`, scatterlist mapping iterators, and the `sunplus,sp7021-mmc` compatible.

Risks: DMA supports at most eight mapped sectors and treats too many segments as `-EINVAL`; callers rely on MMC limits to avoid that path. The tuning scan breaks after the first passing delay, so the "best delay" helper rarely sees a full pass window. Error handling mutates delay fields and gives commands many retries, which can hide marginal timing faults. Reset has a documented DMA-idle workaround and ignores timeout return in one path. PIO assumes 4-byte FIFO accesses and can leave partial-transfer failures reflected only through status polling.

Test signals: useful checks are successful probe and card enumeration, clean request completion in synchronous DMA, interrupt-driven DMA, and PIO modes, correct R2 response decoding, multi-block STOP behavior, CRC/timeout recovery with reset and retune, GPIO card-detect behavior, runtime PM clock gating, and high-speed/DDR timing transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sunplus-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sunxi-mmc.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sunxi-mmc.c

Purpose: this is the Allwinner Sunxi MMC/SD/SDIO host driver. It drives the vendor controller directly, including reset, IDMAC descriptor setup, clock phase/new-timing programming, voltage switching, SDIO IRQs, runtime PM, and SoC-specific capability quirks across many Allwinner compatibles.

Important APIs, types, and functions: `struct sunxi_mmc_cfg` captures descriptor sizing, clock-delay tables, calibration support, DATA0 masking, and new-timing behavior. `struct sunxi_mmc_host` stores clocks, reset, IRQ state, coherent descriptor memory, current request, manual-stop request, regulator state, and timing mode. Key functions are `sunxi_mmc_probe()`, `sunxi_mmc_resource_request()`, `sunxi_mmc_init_host()`, `sunxi_mmc_request()`, `sunxi_mmc_irq()`, `sunxi_mmc_finalize_request()`, `sunxi_mmc_handle_manual_stop()`, `sunxi_mmc_clk_set_rate()`, and `sunxi_mmc_runtime_suspend()/resume()`.

Control flow: probe allocates an MMC host, gathers SoC match data, regulators, MMIO, clocks, reset, and IRQs, enables the controller, allocates one page of coherent IDMAC descriptors, detects old/new timing mode, sets MMC limits and capabilities, parses DT, masks unsupported high-speed modes, initializes registers, enables runtime PM, and registers the host. Requests map the scatterlist for DMA, compose command and interrupt masks, start IDMAC for data, store `host->mrq`, and write argument/command registers under a spinlock. The hard IRQ accumulates masked controller and IDMAC interrupt bits, waits for both command/data and RX DMA completion when needed, finalizes successful or failed requests, and wakes the threaded handler when a data error needs a manual STOP/abort command.

State and persistence: software state includes `int_sum`, `sdio_imask`, `wait_dma`, `ferror` from clock/power setup, `manual_stop_mrq`, `vqmmc_enabled`, and `use_new_timings`. Persistent hardware state is the global control, IDMAC descriptor base, clock control, timing, delay, FIFO threshold, and interrupt mask registers. Runtime suspend disables the IRQ, resets the controller, gates clocks, and asserts reset; resume reenables clocks, reinitializes registers, restores bus width/clock, and reenables the IRQ.

Dependencies and integration points: the driver integrates with MMC DT parsing, regulators, GPIO CD/RO helpers, runtime PM, common clock and `sunxi-ng` MMC timing-mode helpers, reset controls, coherent DMA, threaded IRQs, and compatibles from `allwinner,sun4i-a10-mmc` through A64/A100/H616/D1 variants.

Risks: IDMAC requires 4-byte-aligned scatterlist offsets and lengths; failures after `dma_map_sg()` can return without unmapping in the map helper path. Manual STOP recovery is deliberately outside the spinlock but depends on a single outstanding request. Clock updates use long polling windows and DATA0 masking on selected SoCs. New-timing and calibration behavior is SoC-specific and partly documented as uncertain. Runtime suspend disables IRQs to avoid fake interrupts while clocks are off, so wake behavior depends on the PM/card-detect configuration.

Test signals: validate probe for old-timing, switchable-timing, and new-timing-only SoCs; DMA read/write and unaligned-rejection paths; manual STOP after data errors; SDIO IRQ enable/disable with runtime PM references; regulator voltage switching; DDR52 and high-speed phase selection; runtime/system suspend/resume; and expected masking of HS/DDR/HS400 capabilities by compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sunxi-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/tifm_sd.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/tifm_sd.c

Purpose: this is the TI FlashMedia SD socket driver. It plugs a `tifm_dev` socket into the MMC core, supporting SD commands, 4-bit mode, FIFO PIO fallback, socket DMA with a one-block bounce buffer, request timeout/eject handling, and card/data event callbacks supplied by the TIFM bus layer.

Important APIs, types, and functions: `struct tifm_sd` tracks the socket, current request, command flags, clock settings, DMA/PIO decision, scatterlist position, block offset, bounce buffer, completion work, and request timer. MMC operations are `tifm_sd_request()`, `tifm_sd_ios()`, and `tifm_sd_ro()`. The event-driven core is `tifm_sd_card_event()`, `tifm_sd_data_event()`, `tifm_sd_check_status()`, `tifm_sd_end_cmd()`, and `tifm_sd_abort()`, with data helpers for FIFO access, bounce copying, and DMA segment programming.

Control flow: probe checks socket occupancy, allocates the MMC host, sets request limits and capabilities, wires the socket's `card_event` and `data_event` callbacks, initializes the controller, and calls `mmc_add_host()`. A request rejects ejected or concurrent work, chooses PIO for non-power-of-two block sizes or the `no_dma` module parameter, maps DMA and the bounce block when possible, programs block count/length and timeouts, lights the LED, arms a one-second timer, and executes the command. Socket events update command/data/stop readiness, program additional DMA chunks, move FIFO data, collect responses, and queue bottom-half work when complete. The bottom half deletes the timer, unmaps DMA, computes `bytes_xfered`, clears the LED, and completes the request.

State and persistence: state is per-socket and volatile: `eject`, `open_drain`, `no_dma`, `cmd_flags`, `clk_freq`, `clk_div`, `req`, scatterlist cursors, and bounce data. Module parameters `no_dma` and `fixed_timeout` persist for the loaded module and change transfer mode or timeout programming. Resume reinitializes the controller and marks the socket ejected on failure.

Dependencies and integration points: the driver depends on the TIFM core for socket discovery, locks, DMA mapping helpers, event dispatch, and eject handling. It uses MMC host APIs, scatterlists, local page mappings, timers, `system_bh_wq`, and module init/exit registration through `tifm_register_driver()`.

Risks: the driver uses a fixed one-second request timeout and ejects the socket on timeout, which is coarse for long busy operations. DMA requires block-size assumptions and bounce handling for partial blocks; PIO has byte carry logic because the FIFO is effectively 16-bit behind 32-bit accesses. Completion state is spread across interrupt callbacks, timer, and workqueue under the socket lock. `fixed_timeout` disables adaptive data timeout programming. Remove queues completion for an in-flight request while tearing down, so ordering around `cancel_work_sync()` and `mmc_remove_host()` is important.

Test signals: card insertion/removal through TIFM, successful controller reset/initial command, DMA read/write with multi-segment scatterlists, fallback PIO for odd block sizes, timeout/eject behavior, stop-command sequencing for writes and reads, write-protect reporting, suspend/resume reinitialization, and clean unmap/LED cleanup on normal and error completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/tifm_sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc.h

Purpose: this header defines the shared TMIO/MMC host register interface and private host contract used by `tmio_mmc_core.c` and SoC wrapper drivers. It centralizes register offsets, status and mask bits, card-option flags, SDIO IRQ bits, DMA-enable bits, host state, callback hooks, exported core APIs, and bus-shift-aware MMIO helpers.

Important APIs, types, and functions: `struct tmio_mmc_dma_ops` abstracts DMA start, enable, request, release, abort, data-end, optional end, and DMA IRQ handling. `struct tmio_mmc_host` is the shared runtime object with command/request/data pointers, PIO scatterlist cursors, DMA channels and bounce storage, delayed reset and done work, IRQ masks, clock cache, locks, native hotplug and SDIO state, mandatory clock callbacks, optional platform hooks, and DMA ops. Public entry points declared here include `tmio_mmc_host_alloc()`, `tmio_mmc_host_probe()`, `tmio_mmc_host_remove()`, `tmio_mmc_do_data_irq()`, IRQ mask helpers, `tmio_mmc_irq()`, and runtime PM helpers.

Control flow: wrapper drivers allocate or embed platform data, call `tmio_mmc_host_alloc()`, fill callbacks and flags, request an IRQ using `tmio_mmc_irq()`, and then call `tmio_mmc_host_probe()`. During operation, the core uses the inline accessors to read/write registers at `host->ctl + (addr << host->bus_shift)`, allowing 16-bit logical TMIO registers to be placed on wider SoC address maps. The write helper for 16-bit registers optionally invokes `write16_hook()` to let a platform veto writes during idle-wait quirks.

State and persistence: the header itself stores no state, but it defines which state survives in the host: IRQ masks, cached clock, DMA channels, current request pointers, scatterlist offsets, and platform callbacks. Register definitions describe persistent hardware state such as command, response, status, clock control, transfer length/count, card options, SDIO masks, DMA enable, reset, version, and SoC-specific mode/status registers.

Dependencies and integration points: it includes Linux MMC host APIs, platform devices, scatterlists, workqueues, DMAEngine, and `linux/mfd/tmio.h`. It is the contract between generic TMIO core code and wrappers such as UniPhier or Renesas SDHI variants.

Risks: register access width and `bus_shift` must match the wrapper's hardware, or every register access lands incorrectly. `sd_ctrl_write32_as_16_and_16()` adds `sdcard_irq_setbit_mask` for IRQ/status writes, so platform masks must be correct. Optional callbacks are invoked from mixed contexts; wrappers must honor locking and sleepability expectations. Host state exposes raw pointers for current request/data, so core/wrapper ownership conventions matter.

Test signals: compile coverage with multiple TMIO wrappers, correct register spacing on bus-shifted SoCs, SDIO IRQ mask behavior, DMA ops fallback to PIO, runtime PM callback linkage, and wrapper-specific reset/clock/write-hook interactions through the common exported functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc_core.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc_core.c

Purpose: this is the generic TMIO MMC core shared by several platform wrappers. It implements the MMC host operations, command/data state machine, PIO transfers, optional DMA handoff, SDIO/native hotplug IRQ handling, regulator power sequencing, reset and timeout recovery, host allocation/probe/remove, and runtime PM helpers.

Important APIs, types, and functions: exported APIs include `tmio_mmc_host_alloc()`, `tmio_mmc_host_probe()`, `tmio_mmc_host_remove()`, `tmio_mmc_irq()`, `tmio_mmc_do_data_irq()`, IRQ enable/disable helpers, and runtime suspend/resume. The MMC-facing operations are `tmio_mmc_request()`, `tmio_mmc_set_ios()`, `tmio_mmc_get_ro()`, `tmio_mmc_get_cd()`, `tmio_mmc_enable_sdio_irq()`, and `tmio_multi_io_quirk()`. Internal control is split across `tmio_mmc_start_command()`, `tmio_mmc_start_data()`, `tmio_mmc_cmd_irq()`, `tmio_mmc_data_irq()`, `tmio_mmc_pio_irq()`, `tmio_mmc_finish_request()`, and `tmio_mmc_reset_work()`.

Control flow: allocation maps the controller resource, allocates the MMC host, copies generic ops into `host->ops`, parses DT, and stores driver data. Probe validates clock limits, resolves OCR/regulators/GPIO CD/RO, sets host capabilities and request limits, determines native hotplug, resets the controller, initializes locks/work, requests DMA via wrapper ops, enables runtime PM, and registers the MMC host. Requests set `host->mrq`, optionally start data, issue SBC or main command, and arm delayed reset work. IRQ handling reads/acks status, dispatches card-detect, command, PIO, data-end, DMA, and SDIO events. Completion cancels timeout work, ends/aborts DMA, optionally continues from SET_BLOCK_COUNT to the main command, applies platform fixups/retune checks, and calls `mmc_request_done()`.

State and persistence: persistent software state includes current command/data/request pointers, scatterlist cursor, DMA-on flag, cached IRQ masks, clock cache, native hotplug hold, SDIO IRQ state, and delayed recovery work. Hardware state is reset on probe, runtime resume, selected errors, and power-off paths, while optionally preserving bus width, clock, and SDIF mode during recovery resets. Runtime suspend disables MMC IRQs, stops the card clock, and calls wrapper clock-disable; resume reenables clocks, resets, restores cached clock, and reenables DMA.

Dependencies and integration points: the core depends on wrapper-supplied `tmio_mmc_data` flags/capabilities, clock callbacks, optional reset/write/fixup/retune/timeout/SDIO hooks, and optional `tmio_mmc_dma_ops`. It integrates with regulators, GPIO descriptors, runtime PM, dev PM QoS, DMAEngine abstractions, and the MMC retune and SDIO IRQ APIs.

Risks: request, `.set_ios()`, timeout recovery, and workqueue completion coordinate through `host->mrq` sentinel error pointers; mistakes can produce dropped or duplicate completions. PIO handles 16/32/64-bit data ports and odd-byte tails with little-endian assumptions. Auto-CMD12 support is limited and logs unsupported stop commands. Native hotplug intentionally holds a runtime PM reference. DMA callbacks may complete data under `host->lock`, so wrapper ops must match the locking contract.

Test signals: exercise command-only, single-block, multi-block with and without SBC, PIO read/write on all data-port widths, DMA start/dataend/abort paths, delayed reset after missing IRQs, SDIO IRQ enable/disable and signaling, native and GPIO card detect, regulator power transitions, runtime suspend/resume with cached clock restore, and wrapper fixup/retune hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/toshsd.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/toshsd.c

Purpose: this is a legacy Toshiba PCI Secure Digital host driver. It drives the Toshiba-specific PCI/MMIO SD controller directly, using PIO data transfers, card-detect interrupts, PCI config-space clock/power/LED controls, and simple suspend/resume powerdown.

Important APIs, types, and functions: `struct toshsd_host` comes from `toshsd.h` and stores the PCI device, MMC host, lock, current request/command/data, scatterlist mapping iterator, and MMIO base. MMC operations are `toshsd_request()`, `toshsd_set_ios()`, `toshsd_get_ro()`, and `toshsd_get_cd()`. Core helpers are `toshsd_init()`, `__toshsd_set_ios()`, `toshsd_irq()`, `toshsd_thread_irq()`, `toshsd_cmd_irq()`, `toshsd_data_end_irq()`, `toshsd_start_cmd()`, `toshsd_start_data()`, and `toshsd_powerdown()`.

Control flow: PCI probe enables the device, allocates an MMC host, requests PCI regions, maps BAR0, sets 4-bit and OCR capabilities plus clock limits, initializes the controller, requests a shared threaded IRQ, and registers the host. Requests reject absent cards, store `host->mrq`, initialize PIO scatterlist iteration for data, enable the activity LED, and write command/argument registers. The hard IRQ handles errors, card insertion/removal, command response completion, data-end completion, and wakes the threaded IRQ for FIFO read/write readiness. The thread transfers one block-sized chunk through `SD_DATAPORT` using 32-bit repeated IO and updates the scatterlist iterator. Completion clears request pointers, LED state, and calls `mmc_request_done()`.

State and persistence: runtime state is the current MMC request, command/data pointers, SG iterator, and controller register contents. PCI config space carries clock-stop, divider mode, power, card-detect, and LED setup. Suspend masks interrupts, disables SD/SDIO clocks, powers down the card, stops the PCI clock, saves PCI state, and enters D3hot; resume restores PCI state, reenables the device, and reinitializes hardware.

Dependencies and integration points: the driver uses PCI core APIs, raw MMIO accessors, MMC host APIs, scatterlist mapping iterators, shared/threaded IRQs, and register constants from `toshsd.h`. It binds PCI vendor/device `0x1179:0x0805`.

Risks: no DMA is used, so throughput and CPU use depend on interrupt-per-block PIO. The STOP command path fakes immediate completion for `MMC_STOP_TRANSMISSION`, while multi-block normal data uses auto CMD12 register setup. Non-timeout errors reinitialize the controller inside IRQ handling and then rely on later IOS restoration. The threaded handler returns `IRQ_NONE` for a spurious data IRQ after potentially completing an errored command. Clock division from `HCLK` cannot produce common full SD/MMC rates.

Test signals: probe on the matching PCI device, card insert/remove interrupts and polling state, PIO read/write integrity for single and multi-block transfers, response decoding for R2 and short responses, timeout/CRC/error register logging and recovery, write-protect reporting, LED activity, and suspend/resume restoring enumeration and clock/power state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/toshsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/toshsd.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/toshsd.h

Purpose: this header describes the Toshiba PCI SD controller register map and the driver's private host structure. It is paired with `toshsd.c` and contains PCI config-space offsets, SD/SDIO MMIO register offsets, clock/power/card option bits, command encoding values, interrupt/status/error masks, and `struct toshsd_host`.

Important APIs, types, and functions: there are no functions exported from this header. The central type is `struct toshsd_host`, which owns the PCI and MMC device pointers, spinlock, current request/command/data pointers, `sg_mapping_iter` for PIO, and mapped MMIO base. Important constants include PCI clock/power/LED registers (`SD_PCICFG_*`), SD command/data/status registers (`SD_CMD`, `SD_CARDSTATUS`, `SD_DATAPORT`, `SD_INTMASKCARD`), SDIO offsets, clock divider bits, card option flags, response command encodings, STOP/internal action flags, and detailed error masks.

Control flow: `toshsd.c` uses these definitions to initialize PCI config space and MMIO registers, compose commands in `toshsd_start_cmd()`, set bus clock/power/width in `__toshsd_set_ios()`, identify card/status/data interrupts in `toshsd_irq()`, and decode detailed error status for logging. The `IRQ_DONT_CARE_BITS` mask filters status bits that should not drive IRQ dispatch.

State and persistence: the header defines where persistent hardware state lives: PCI config bytes hold clock stop/gate/mode, power, card-detect, slot, and LED controls; MMIO registers hold active commands, arguments, responses, card status, interrupt masks, transfer length/count, options, data port, transaction control, and software reset. The host structure stores volatile software state only.

Dependencies and integration points: it depends on kernel bit macros and MMC/PCI types through the C file includes. Its constants align the Toshiba-specific hardware with the generic MMC host callbacks implemented in `toshsd.c`.

Risks: many constants encode poorly documented hardware behavior, including duplicated card-present bits, SDIO-base aliases, and detailed error fields spanning two status registers. Width/timeout/card-option values are hard-coded by the driver. Any mismatch in these definitions directly affects raw MMIO and PCI config writes.

Test signals: compile coverage of `toshsd.c`, correct interrupt masking with `IRQ_DONT_CARE_BITS`, expected command and response encodings on real hardware, card option writes for 1-bit and 4-bit bus modes, error-detail logs matching injected CRC/timeout faults, and power/clock/LED config writes during probe, IOS changes, suspend, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/toshsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/uniphier-sd.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/uniphier-sd.c

Purpose: this is the Socionext UniPhier SD/eMMC wrapper around the TMIO MMC core. It supplies UniPhier clock/reset control, register spacing, internal or external DMA implementations, UHS voltage/pinctrl/syscon handling, eMMC hardware reset, and compatible-specific quirks.

Important APIs, types, and functions: `struct uniphier_sd_priv` embeds `struct tmio_mmc_data` and stores pinctrl states, clock, resets, DMA channel, DMA direction, syscon regmap/channel, clock rate, and capability flags. DMA is implemented through two `tmio_mmc_dma_ops` tables: `uniphier_sd_external_dma_ops` for older external DMAEngine use and `uniphier_sd_internal_dma_ops` for extended-IP internal DMA registers. Other key functions are `uniphier_sd_clk_enable()/disable()`, `uniphier_sd_set_clock()`, `uniphier_sd_host_init()`, `uniphier_sd_start_signal_voltage_switch()`, `uniphier_sd_uhs_init()`, `uniphier_sd_probe()`, and `uniphier_sd_remove()`.

Control flow: probe gets the IRQ, allocates private data, reads compatible capability flags, acquires clock and reset controls, initializes TMIO platform data flags, allocates the TMIO host, installs eMMC hardware-reset and UHS voltage hooks when advertised by DT caps, chooses internal or external DMA ops, sets `bus_shift = 1` and clock callbacks, enables clocks/resets, initializes UniPhier host-mode and clock-control registers, sets OCR/max segment/block limits, masks IRQs, requests `tmio_mmc_irq()`, and delegates registration to `tmio_mmc_host_probe()`. Runtime request/control flow is mostly TMIO core code; UniPhier callbacks program clock divisors, speed mode, voltage, DMA enable, DMA start, and DMA data-end completion.

State and persistence: persistent wrapper state includes `clk_rate`, selected DMA channel/fake channel markers, `dma_dir`, syscon UHS channel, and capability flags such as extended IP or broken RX DMA. Hardware state spans host-mode, clock-control, voltage, DMA mode/control/reset/address registers, reset lines, and syscon UHS/SDR mode bits. Remove unregisters the TMIO host and disables wrapper clocks/resets.

Dependencies and integration points: this driver integrates with `tmio_mmc_core`, DMAEngine, coherent/raw MMIO DMA registers, regmap/syscon, pinctrl, clocks, reset controls, OF match data, and MMC UHS/hw-reset capabilities. Compatibles distinguish v2.91, v3.1 with broken RX DMA, and v3.1.1 extended IP.

Risks: external DMA delays enabling `TMIO_STAT_DATAEND` until the DMA callback because hardware may assert DATAEND before DMA starts. Internal DMA only supports one SG segment and 8-byte-aligned offsets; otherwise it falls back to PIO. Fake DMA channel pointers mark internal DMA availability and must not be released as real channels. UHS setup is disabled if pinctrl/syscon setup fails. Clock divisors are rounded to power-of-two encodings with UniPhier-specific 1/1 and 1/1024 bits.

Test signals: probe all compatibles, confirm TMIO register spacing via `bus_shift`, verify external DMA callback ordering, internal DMA read fallback on broken-RX variants, PIO fallback for multi-SG or unaligned requests, UHS 1.8 V pinctrl/syscon transitions, eMMC reset pulse timing, clock rate/divisor behavior, and TMIO runtime suspend/resume through wrapper clock callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/uniphier-sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/usdhi6rol0.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/usdhi6rol0.c

Purpose: this is the Renesas USDHI6ROL0 SD/SDIO host driver. It implements a full custom MMC host state machine with command/data/stop phases, PIO scatterlist page mapping and bounce buffering, optional DMAEngine transfers, SDIO and card-detect IRQs, voltage pinctrl switching, clock/power setup, and timeout recovery.

Important APIs, types, and functions: `enum usdhi6_wait_for` describes the active state machine phase. `struct usdhi6_host` stores current request, MMIO base, clock, SG/page/bounce state, IRQ masks/status, app-command tracking, timeout work, DMA channels/active flag, and pinctrl. MMC ops are `usdhi6_request()`, `usdhi6_set_ios()`, `usdhi6_get_cd()`, `usdhi6_get_ro()`, `usdhi6_enable_sdio_irq()`, `usdhi6_sig_volt_switch()`, and `usdhi6_card_busy()`. Core helpers include `usdhi6_rq_start()`, `usdhi6_cmd_flags()`, `usdhi6_sd()/usdhi6_sd_bh()`, `usdhi6_blk_read()/write()`, `usdhi6_sg_map()/unmap()/advance()`, and the DMA setup/completion helpers.

Control flow: probe requires OF, gets named data and SDIO IRQs plus optional card-detect IRQ, allocates and parses the MMC host, obtains pinctrl, maps MMIO, enables the clock, validates the version register, masks interrupts, requests IRQs, initializes timeout work, requests DMA channels, sets host caps/limits and clock range, and registers the MMC host. A request stores `host->mrq`, programs timeout, prepares DMA or PIO state, writes block counts/options/argument/command, sets `wait = USDHI6_WAIT_FOR_CMD`, and schedules timeout work. The hard IRQ masks back to card-detect-only, acks status, records error/status bits, and wakes the threaded bottom half. The bottom half advances the state through response, PIO block read/write, DMA completion, data end, optional STOP, and final `mmc_request_done()`.

State and persistence: software state is rich and request-scoped: `wait`, `app_cmd`, current SG/page mappings, cross-page bounce fields, DMA active/channel state, `io_error`, `irq_status`, and timeout work. Persistent hardware state includes clock divider/enables, option width/timeout bits, SDIF DDR mode, CC external DMA mode, interrupt masks, SDIO mask/mode, and regulator/pinctrl voltage state. Remove masks IRQs, cancels timeout work, releases DMA, and disables the clock.

Dependencies and integration points: the driver uses platform/OF resources, MMC regulators and DT parsing, pinctrl default/UHS states, DMAEngine slave channels named `tx` and `rx`, delayed work, threaded IRQs, and direct MMIO. It binds `renesas,usdhi6rol0`.

Risks: the state machine is sensitive to missing IRQs and uses a fixed 4-second timeout. DMA failures release DMA channels and fall back to PIO for later transfers. PIO mapping handles cross-page blocks with bounce buffers, but large SG segments keep the code complex. Response selection for multi-block commands avoids auto-CMD12 conflicts by reading a different response register. Voltage switching warns but continues after pinctrl failures. There are no explicit runtime PM callbacks.

Test signals: version detection, card-detect IRQ or polling fallback, SDIO IRQ masking/signaling, command-only and APP_CMD flows, single/multi-block PIO including cross-page blocks, DMA read/write and fallback on DMA errors, STOP response handling, timeout recovery in each `wait` state, regulator/pinctrl voltage switching, DDR clock/bus-width setup, and remove while idle after active transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/usdhi6rol0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/ushc.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/ushc.c

Purpose: this is a USB SD Host Controller driver for the CSR Astoria-style USB SD controller. It exposes the USB device as an MMC host by translating MMC requests into a vendor-specific control/bulk protocol with command block wrappers, optional data URBs, command status wrappers, and an interrupt URB for card/SDIO status.

Important APIs, types, and functions: vendor requests are modeled by `enum ushc_request` and `enum ushc_request_type`. `struct ushc_cbw`, `struct ushc_csw`, and `struct ushc_int_data` describe the USB protocol payloads. `struct ushc_data` stores the USB device, MMC host, interrupt/CBW/data/CSW URBs and buffers, current request, capabilities, host-control shadow, flags, last interrupt status, and current clock. MMC ops are `ushc_request()`, `ushc_set_ios()`, `ushc_get_cd()`, and `ushc_enable_sdio_irq()`.

Control flow: probe validates endpoints, allocates the MMC host and private state, resets the USB controller, reads capabilities, sets MMC caps/limits, allocates and fills interrupt, CBW, data, and CSW URBs, registers the MMC host, and submits the persistent interrupt URB. A request rejects disconnected devices, unsupported R2 responses, and data transfers below 6 MHz, then fills and submits a CBW bulk OUT URB, optionally submits one SG-backed data bulk URB, and submits the CSW bulk IN URB. Completion callbacks unlink dependent URBs on failure; `csw_callback()` translates command/data status bits to MMC errors, fills response word 0, sets `bytes_xfered`, and completes the request. The interrupt callback tracks card-present changes and SDIO IRQ status, handles the ignore-next interrupt rule, and resubmits itself.

State and persistence: persistent state includes `caps`, `host_ctrl`, `clock_freq`, `last_status`, SDIO interrupt enable/ignore flags, and allocated URBs. The current request pointer is used by asynchronous CSW completion. Disconnect sets `DISCONNECTED`, kills all URBs, removes the MMC host, and frees protocol buffers.

Dependencies and integration points: the driver integrates with USB core URB/control-message APIs and the MMC host core. It uses vendor/product `0x0a12:0x5d10`, bulk endpoint pipes 2 and 6 for command/data/status, and the interface interrupt endpoint for card/SDIO events.

Risks: firmware version 2 lacks R2 response support, so CID/CSD-style requests with 136-bit responses are rejected. The driver supports only one data SG segment and sets `max_segs = 1`. The same bulk pipes are used for command/status and data directions, making URB ordering and unlinking important. Clock-off is coerced to 400 kHz because interrupts require a clock. Data transfers below 6 MHz are rejected due to FIFO limitations. Error mapping collapses CRC errors to `-EIO` rather than `-EILSEQ`.

Test signals: USB probe/reset/capability read, interrupt URB resubmission and card-detect changes, SDIO IRQ enable/ignore-next behavior, command-only request completion, data read/write at valid clocks with one SG segment, rejection of R2 and low-clock data requests, URB failure unlink paths, high-speed host-control changes, and disconnect during idle or active requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/ushc.c -->
