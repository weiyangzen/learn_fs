# Research Group subset-b-004271

This grouped research report covers the requested MMC host files under `sources/distributed-fs/ceph-client/drivers/mmc/host`. Each section is source-path aligned for reconciliation into final per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc.h

## Purpose

`dw_mmc.h` is the shared private interface for the Synopsys DesignWare MMC/SD/SDIO host controller driver family. It does not implement a platform driver itself; it defines the controller state object, common state-machine/event enums, DMA hooks, register offsets, bit definitions, FIFO access helpers, exported core entry points, and per-SoC extension callbacks consumed by DesignWare MMC core and platform-specific glue.

## Important APIs, Types, And Functions

- `enum dw_mci_state` models the bottom-half request state machine: idle, command send, data send, data busy, stop send, data error, CMD11 voltage-switch states.
- `enum dw_mci_cookie` tracks DMA mapping ownership for MMC requests: unmapped, pre-mapped by `pre_req`, and mapped by transfer preparation.
- `enum { TRANS_MODE_PIO, TRANS_MODE_IDMAC, TRANS_MODE_EDMAC }` identifies the selected transfer backend.
- `struct dw_mci_dma_slave` carries an external DMA channel and direction.
- `struct dw_mci` is the central host state. It holds MMIO pointers, current `mmc_request`/`mmc_command`/`mmc_data`, stop command storage, DMA buffers and ops, command/data status snapshots, workqueue/event bitmaps, clocks, reset controller, FIFO push/pull state, timers, quirks, IRQ metadata, slot/host references, and clock phase map.
- `struct dw_mci_dma_ops` defines the DMA backend contract: `init`, `start`, `complete`, `stop`, `cleanup`, and `exit`.
- `struct dw_mci_drv_data` is the variant hook table for capabilities, initialization, DT parsing, tuning, HS400 preparation, voltage switch, timeout programming, DRTO calculation, and hardware reset.
- `mci_readl()` and `mci_writel()` wrap relaxed access to named `SDMMC_*` registers.
- `mci_fifo_readw/l/q()` and `mci_fifo_writew/l/q()` provide raw FIFO access. `mci_fifo_l_readq()` and `mci_fifo_l_writeq()` emulate 64-bit FIFO access as two 32-bit accesses for controllers with `DW_MMC_QUIRK_FIFO64_32`.
- External core functions are declared: `dw_mci_alloc_host`, `dw_mci_probe`, `dw_mci_remove`, `dw_mci_runtime_suspend`, and `dw_mci_runtime_resume`.

## Control Flow And State

The header documents the state model expected by implementation files. Interrupt handlers snapshot controller status into `cmd_status` and `data_status`, set bits in `pending_events`, and the `bh_work` worker advances `state` while updating `completed_events`. Active request pointers (`mrq`, `cmd`, `data`) and state are guarded by `host->lock`; interrupt-mask updates are isolated under `irq_lock`. The comments emphasize ordering before setting event bits: data interrupts must be disabled and status captured before `EVENT_DATA_*`, command-ready interrupt must be disabled and status captured before `EVENT_CMD_COMPLETE`, and bytes transferred must be committed before `EVENT_XFER_COMPLETE`.

DMA state is persistent across a request via `use_dma`, `using_dma`, descriptor ring fields, external DMA slave data, and request cookies. FIFO PIO state persists across partial transfers using `sg`, `sg_miter`, `part_buf_start`, `part_buf_count`, and `part_buf`.

## Dependencies And Integration Points

The header depends on Linux MMC core types, DMAEngine, reset control, fault injection, hrtimers, IRQs, scatterlists, workqueues, and platform driver infrastructure. It integrates DesignWare core logic with SoC-specific wrappers through `dw_mci_drv_data`, with DMA engines through `dw_mci_dma_ops`, with the MMC host core through `struct mmc_host`, and with runtime PM through exported suspend/resume declarations.

Register definitions span the base controller, IDMAC 32-bit and 64-bit descriptor layouts, UHS/DDR/HS400 controls, clock, timeout, interrupt, FIFO threshold, and command formatting fields. Platform code is expected to use these definitions instead of open-coded offsets.

## Risks And Edge Cases

- Locking/order violations around `pending_events`, status snapshots, and interrupt masking can produce lost completions or double completion.
- FIFO endian and width handling is sensitive; the 64-bit FIFO-as-two-32-bit helper exists for controllers that cannot safely use raw 64-bit operations.
- `mci_fifo_writew()`/`mci_fifo_writel()` macro argument order is unusual because the raw write macros take value then register; callers must use the wrapper as defined.
- Timer fields for CMD11, command timeout, and data timeout imply recovery paths outside this header; variant code must coordinate with them.
- `struct dw_mci_drv_data` callbacks are optional, so core code must null-check and provide defaults.

## Test Signals

Useful validation signals include boot/probe of multiple DesignWare variants, PIO and IDMAC/EDMAC transfers, pre_req/post_req DMA mapping reuse, SDIO IRQ delivery, voltage switch CMD11, tuning/HS400 paths, FIFO64_32 quirk coverage on 64-bit kernels, runtime suspend/resume, and fault-injection induced data CRC failures when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/jz4740_mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/jz4740_mmc.c

## Purpose

`jz4740_mmc.c` implements a platform MMC host driver for Ingenic JZ4740-family SD/MMC controllers, covering JZ4740, JZ4725B, JZ4760, JZ4780/JZ4775, and X1000 variants. It supports PIO and optional DMAEngine transfers, SDIO interrupts, regulators, GPIO card-detect/write-protect, signal voltage switching, and simple suspend/resume pinctrl handling.

## Important APIs, Types, And Functions

- Register and bit macros define the Ingenic MSC register map: start/stop/clock, status, clock divider, command attributes, block length/count, IRQ mask/status, command/argument/response FIFO, RX/TX FIFO, low-power mode, and JZ4780 DMA control.
- `enum jz4740_mmc_version` selects register width behavior and SoC quirks.
- `enum jz4740_mmc_state` drives threaded IRQ handling: read response, transfer data, send stop, done.
- `enum jz4780_cookie` tracks DMA mapping state for `pre_req`/`post_req` and in-flight IRQ mapping.
- `struct jz4740_mmc_host` stores the host, platform device, clock, variant, IRQ, MMIO base/resource, current request/command, vqmmc state, wait bit, cached `cmdat`, IRQ mask, timeout timer, scatterlist iterator, state, DMA channels, and DMA mode flag.
- `jz4740_mmc_acquire_dma_channels()` supports either a unified `"tx-rx"` channel or separate `"tx"` and `"rx"` channels and tightens `mmc->max_seg_size` to DMA limits.
- `jz4740_mmc_prepare_dma_data()`, `jz4740_mmc_start_dma_transfer()`, `jz4740_mmc_pre_request()`, and `jz4740_mmc_post_request()` implement DMA mapping, descriptor submission, and cleanup.
- `jz4740_mmc_write_data()` and `jz4740_mmc_read_data()` implement PIO FIFO transfers using `sg_mapping_iter` and FIFO request interrupts.
- `jz_mmc_irq()` is the hard IRQ handler; `jz_mmc_irq_worker()` is the threaded state-machine worker.
- `jz4740_mmc_set_ios()`, `jz4740_mmc_set_clock_rate()`, `jz4740_voltage_switch()`, and `jz4740_mmc_enable_sdio_irq()` implement the `mmc_host_ops` control plane.
- `jz4740_mmc_probe()` allocates/configures the host, resources, IRQ, DMA, limits, regulators, and registers with the MMC core.

## Control Flow And State

Requests start in `jz4740_mmc_request()`: the driver stores `host->req`, clears IRQ status, enables `END_CMD_RES`, sets state to `READ_RESPONSE`, arms a 5-second timer, and writes command registers through `jz4740_mmc_send_command()`. The hard IRQ reads status and IRQ flags, handles SDIO IRQs immediately, and when a waited command/data event arrives disables the IRQ source, clears the wait bit/timer, records command/data errors, and wakes the threaded handler.

The threaded handler reads the command response, prepares data iteration, then transfers data through DMA or PIO. DMA mode submits the transfer after mapping and optimistically sets `bytes_xfered`; PIO loops over FIFO request events. After data transfer it polls for `DATA_TRAN_DONE`, optionally sends a stop command and waits for program-done for busy stops, then calls `jz4740_mmc_request_done()`.

Timeout state is persisted in `host->waiting` bit 0 and `timeout_timer`. If a polled IRQ does not arrive quickly, `jz4740_mmc_poll_irq()` enables the hardware IRQ and arms the timer; the timeout handler disables command-end IRQ, marks the command timed out, and completes the request.

Power and bus state are cached in `host->cmdat` and `host->vqmmc_enabled`. `set_ios` resets on power-up, enables/disables regulators and clocks, sets the initialization bit for the next command, and updates bus-width bits.

## Dependencies And Integration Points

The driver integrates with Linux platform devices, OF match data, MMC core (`mmc_of_parse`, `mmc_add_host`, `mmc_request_done`), GPIO slot helpers, regulator supply helpers, DMAEngine, clocks, pinctrl PM states, threaded IRQs, timers, and scatterlist mapping. It includes `asm/cacheflush.h`, but the visible code path mostly relies on DMA/SG and FIFO access helpers. Device tree compatibles map directly to `enum jz4740_mmc_version`.

## Risks And Edge Cases

- DMA and PIO completion differ: DMA marks all bytes transferred immediately after submission, so data error paths must be caught by controller status and DMA termination.
- `jz4740_mmc_post_request()` assumes `data` is valid in the error branch; callers normally provide data for pre/post paths, but null handling is partial.
- Poll-to-IRQ fallback depends on `host->waiting` and timer ordering. Races could double-complete if an IRQ and timer cross, though the bit test mitigates this.
- Fixed `max_busy_timeout` is 5 seconds and the code comments call out that it does not honor per-command busy timeout yet.
- Version-specific IRQ register width and DMA control location are critical for older versus JZ4780+ SoCs.
- The JZ4760 maximum clock is clamped to 24 MHz due to known reliability issues.

## Test Signals

Validation should cover all compatible variants, 1/4/8-bit bus modes where advertised, PIO fallback when DMA channels are unavailable, unified and split DMA channel configurations, DMA pre_req/post_req paths, SDIO IRQ signaling, command/data CRC and timeout handling, stop commands after multi-block transfers, card-detect/write-protect GPIOs, vmmc/vqmmc regulator transitions, and suspend/resume pinctrl state selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/jz4740_mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/litex_mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/litex_mmc.c

## Purpose

`litex_mmc.c` implements an MMC host driver for LiteX LiteSDCard gateware. It exposes LiteX PHY/core/reader/writer/IRQ CSR regions as an MMC host, using LiteX CSR accessors and DMA-capable memory addresses for block transfers. The driver is tailored to SD cards, forcing 4-bit mode and disabling SDIO/MMC card types through capabilities.

## Important APIs, Types, And Functions

- Register macros describe LiteX PHY, core command/data event, reader DMA, writer DMA, and interrupt CSR offsets.
- Protocol constants encode LiteSDCard command transfer direction, response length, event bits, polling timeouts, and IRQ bits.
- `struct litex_mmc_host` stores mapped CSR regions, coherent bounce buffer and DMA address, command completion, IRQ, reference and SD clock values, raw response words, relative card address, and state flags for bus-width injection and APP_CMD tracking.
- `litex_mmc_sdcard_wait_done()` polls event registers and maps done, write error, timeout, and CRC bits to Linux errors.
- `litex_mmc_send_cmd()` writes command argument/configuration, optionally waits for IRQ completion, validates command and data event registers, copies response words, tracks RCA and APP_CMD state, and waits for reader/writer DMA done.
- `litex_mmc_set_bus_width()` injects `APP_CMD` and `SD_APP_SET_BUS_WIDTH` before first data transfer because the hardware only supports 4-bit transfers and needs that programming earlier than the generic core may do it.
- `litex_mmc_do_dma()` maps the request scatterlist. If a single DMA segment is available it programs hardware directly; otherwise it uses a coherent bounce buffer and copies write/read data.
- `litex_mmc_request()` sequences optional SBC, early bus-width setup, DMA programming, command retry, response translation, optional stop command, DMA unmap, data copy-back, and request completion.
- `litex_mmc_irq_init()` optionally enables card-detect and command-done IRQs; otherwise it marks the host as polling.
- `litex_mmc_probe()` allocates the host, maps named resources, configures DMA mask/bounce buffer, initializes capabilities and limits, parses DT, and adds the host.

## Control Flow And State

The request path is synchronous from the MMC core perspective. `litex_mmc_request()` first verifies card presence, sends SBC if present, performs one-time 4-bit bus setup before data, programs DMA reader/writer, sends the command with retries, translates LiteX response layout to MMC response layout, sends a stop if needed, unmaps DMA, copies bounce reads back, and calls `mmc_request_done()`.

For commands with data or DAT0 busy and a valid IRQ, `litex_mmc_send_cmd()` enables `CMD_DONE` and waits on `host->cmd_done`; otherwise it polls event registers. Card-detect IRQs call `mmc_detect_change()`. Persistent state includes `rca`, `app_cmd`, and `is_bus_width_set`, which allow command injection to preserve SD application-command ordering and reset bus-width setup after card removal or command errors.

## Dependencies And Integration Points

The driver depends on LiteX CSR helpers (`litex_read8/16/32`, `litex_write*`), Linux platform resources by name (`phy`, `core`, `reader`, `writer`, optional `irq`), DMA mapping/coherent allocation, clocks, MMC/SD constants, OF match `"litex,mmc"`, and the MMC core. It uses standard regulator parsing but defaults to 3.3 V if no OCR is available.

## Risks And Edge Cases

- The hardware only supports 4-bit SD-card operation. The driver forcibly sets `MMC_CAP_4_BIT_DATA`, clears 8-bit, and sets `MMC_CAP2_NO_SDIO | MMC_CAP2_NO_MMC`; integration expecting SDIO/MMC will not work.
- `litex_mmc_do_dma()` maps the SG list before deciding direct versus bounce. It relies on later unconditional `dma_unmap_sg()` whenever data exists.
- Bounce buffer size is `mmc->max_req_size * 2` based on defaults; request limit comments warn that changing block count requires recalculating size.
- `wait_for_completion()` has no explicit timeout; command event register polling after wake still catches device-side errors, but lost IRQs could block if IRQ mode is used.
- `is_bus_width_set` is reset on command errors and card removal, which is required but can add hidden command traffic before data transfers.

## Test Signals

Tests should cover polling and IRQ mode, card insertion/removal, first data transfer bus-width injection, APP_CMD ordering around ACMD6, direct single-SG DMA and bounce-buffer multi-SG paths, read copy-back, command retry behavior, optional SBC/stop handling, response layouts for short and long responses, and DT resource naming errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/litex_mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/loongson2-mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/loongson2-mmc.c

## Purpose

`loongson2-mmc.c` implements a platform MMC/SD/SDIO/eMMC host driver for Loongson-2K controllers. It supports multiple SoC variants (`ls2k0300`, `ls2k0500`, `ls2k1000`, `ls2k2000`) through per-platform data covering register range, DMA type, command-data byte reordering, timeout workarounds, and quirks.

## Important APIs, Types, And Functions

- Register macros define the command, response, data, interrupt, DLL, bus-selection, and internal DMA register maps.
- `enum loongson2_mmc_state` models interrupt progress: none, finalize, command sent, response finished, transfer finished, or combined transfer/response wait.
- `struct loongson2_dma_desc` describes internal DMA hardware descriptors with low/high next descriptor and memory address fields.
- `struct loongson2_mmc_host` holds current request, regmap, resource, clock, current clock rate, coherent descriptor memory, DMA completion flag, external DMA channel, stop-command flag, bus width, IRQ lock, current state, and platform data.
- `struct loongson2_mmc_pdata` supplies variant hooks: `reorder_cmd_data`, `fix_data_timeout`, `setting_dma`, `prepare_dma`, and `release_dma`.
- `loongson2_mmc_send_request()` prepares data/DMA, applies variant timeout fixes, sends command, and handles select-card deselect as a special immediate success.
- `loongson2_mmc_irq()` is the hard IRQ state machine for command sent, response timeout/CRC, data CRC/timeout, data finished, and SDIO IRQs.
- `loongson2_mmc_irq_worker()` finalizes responses, unmaps DMA, sends stop commands, sets bytes transferred, clears host state, and completes the request.
- `loongson2_mmc_set_ios()` controls vmmc, reset, interrupt enables, prescaler, DLL mode for DDR timing, and bus width.
- External DMA support is in `loongson2_mmc_prepare_external_dma()`, `ls2k0500_mmc_set_external_dma()`, and `ls2k1000_mmc_set_external_dma()`.
- Internal descriptor DMA support is in `loongson2_mmc_prepare_internal_dma()`, `ls2k2000_mmc_set_internal_dma()`, and `loongson2_mmc_release_internal_dma()`.

## Control Flow And State

`loongson2_mmc_request()` rejects CMD48 on the `ls2k0300` quirk path by completing immediately, then stores the request and calls `loongson2_mmc_send_request()`. Sending configures data registers, maps and starts DMA via the platform hook, optionally waits for TX FIFO full on affected write commands, and programs command argument/control. The command state is selected based on whether data and/or response is expected.

The hard IRQ reads interrupt and data status registers. SDIO IRQs are handled separately by acknowledging and calling `sdio_signal_irq()`. For active requests it transitions state on command-sent and data-finished events, records timeout/CRC errors, and on close invokes `reorder_cmd_data()` before waking the threaded IRQ. The threaded IRQ unmaps data SGs, waits for DMA completion when necessary, reads four response registers, clears command registers, optionally sends the request stop command, calculates `bytes_xfered`, resets host state, and calls `mmc_request_done()`.

Persistent hardware state includes current clock, prescaler, bus width, enabled interrupts, DLL delay programming for DDR modes, variant DMA routing registers, and coherent descriptor memory for internal DMA variants.

## Dependencies And Integration Points

The driver integrates with platform/OF match data, regmap MMIO, optional clocks or `clock-frequency` firmware property, threaded IRQs, DMAEngine for external DMA variants, coherent DMA descriptors for internal DMA variants, MMC slot GPIO helpers, regulators, and SDIO IRQ infrastructure. It uses `bitrev8x4()` and endian conversion to repair protocol data ordering for specific commands.

## Risks And Edge Cases

- `loongson2_mmc_prepare_dma()` sets `cmd->data->error` on failure in `loongson2_mmc_send_request()`; that path assumes `cmd->data` exists when DMA preparation fails.
- Internal DMA allocates one page of descriptors while `mmc->max_segs` is set to 1, keeping descriptor use bounded. Raising `max_segs` would require descriptor memory review.
- Variant reorder hooks mutate mapped scatterlist virtual data using `sg_virt()`, so data buffers must be CPU-addressable as expected.
- The `ls2k0300` CMD48 quirk completes without setting an explicit error, effectively hiding the unsupported operation from upper layers.
- SDIO IRQ enable uses `regmap_update_bits()` with raw `enable` as value rather than a masked bit value; enable values are expected to be 0/1.
- DLL mode silently returns if lock polling fails; no error is propagated to `set_ios`.

## Test Signals

Coverage should include each compatible, external and internal DMA paths, read/write data transfers, stop-command sequencing, data/response CRC and timeout IRQs, SDIO IRQ enable/ack, DDR timing DLL setup, CMD48 quirk behavior, byte-order fixups for ACMD13/22/51/CMD30/SD_SWITCH, TX FIFO full timeout workaround on writes, regulator power cycling, ACPI-style `clock-frequency`, and suspend/resume clock transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/loongson2-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-gx-mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-gx-mmc.c

## Purpose

`meson-gx-mmc.c` implements the Amlogic GX/GXBB/GXL/GXM/AXG SD/eMMC host controller driver. It manages the controller clock tree, descriptor-chain DMA or bounce-buffer transfers, SDIO IRQs, tuning/resampling, voltage switching, and a G12A-style DRAM access quirk that uses the controller's internal SRAM instead of DDR.

## Important APIs, Types, And Functions

- Register macros define clock, delay/adjust, descriptor start, config, status, IRQ, command descriptor, response, and SRAM data-buffer registers.
- `struct meson_mmc_data` captures SoC-specific clock delay masks, always-on bit, adjust register offset, and SDIO sleep bit.
- `struct sd_emmc_desc` is the four-word hardware command/data descriptor.
- `struct meson_host` stores device/MMC pointers, clock handles, current command, request clock and DDR state, DRAM quirk flag, pinctrl clock-gate state, bounce and descriptor DMA buffers, IRQ, pre/post tracking, and SDIO IRQ lock.
- `meson_mmc_clk_init()` creates a controller-local mux and divider clock from `clkin0`/`clkin1`, initializes register defaults, and enables the MMC clock.
- `meson_mmc_clk_set()` gates/ungates the clock safely, programs DDR mode, sets the clock rate, and updates `mmc->actual_clock`.
- `meson_mmc_pre_req()`/`post_req()` choose descriptor-chain mode based on alignment and block constraints and map/unmap SGs.
- `meson_mmc_start_cmd()` builds direct command registers or descriptor-chain entries, handles bounce-buffer copies, and kicks command execution.
- `meson_mmc_irq()` acknowledges SDIO, CRC, timeout, and end-of-chain/status interrupts and wakes the thread for completion.
- `meson_mmc_irq_thread()` copies bounce reads back, follows SBC/main/stop sequencing through `meson_mmc_get_next_command()`, and completes requests.
- `meson_mmc_resampling_tuning()` sweeps resampling delay values with `mmc_send_tuning()`.

## Control Flow And State

Requests enter `meson_mmc_request()`, which checks DRAM-quirk alignment, decides whether pre/post mapping is needed, stops any current descriptor execution, and starts either SBC or the main command. `meson_mmc_start_cmd()` stores `host->cmd`, programs response/data flags, chooses descriptor-chain or bounce-buffer mode, copies write data when needed, writes descriptors/registers with memory barriers, and starts hardware.

Interrupt handling is split: the hard IRQ acks status, handles SDIO IRQs under a spinlock, sets command errors for CRC/timeouts, reads responses, marks bytes transferred on successful data completion, stops descriptors on errors, and wakes the threaded handler. The thread waits for descriptor stop on errors or copies read bounce data on success, then either starts the next command in the request (main after CMD23, stop after multi-block) or calls `meson_mmc_request_done()`.

Clock state persists in `host->req_rate`, `host->ddr`, and `mmc->actual_clock`. Resampling state is held in the adjust register and reset/disabled for legacy and high-speed non-tuned modes. SDIO IRQ enable state is the IRQ_EN register guarded by `host->lock`.

## Dependencies And Integration Points

The driver integrates with platform resources, OF match data, MMC core, GPIO card-detect IRQs, regulators, reset controller, pinctrl clock-gate state, Linux clock framework, DMA coherent allocation/mapping, threaded IRQs, and SDIO IRQ work. Compatible data selects GX v2 or AXG v3 clock delay layouts.

## Risks And Edge Cases

- Descriptor-chain mode is only safe for aligned SG offsets and block-aligned lengths for multi-block/SDIO CMD53 transfers. The driver falls back to bounce mode and warns once when constraints are not met.
- The DRAM access quirk requires 32-bit aligned SG offsets and lengths and limits transfer size to the internal SRAM buffer.
- Clock gating is hardware-sensitive; if the `clk-gate` pinctrl state is absent, the driver uses the controller stop-clock bit, which comments describe as less safe.
- Error paths stop descriptor execution and wait for idle to prevent late IRQs after request completion.
- HS400 is explicitly disabled because reliable support is unclear.
- `host->needs_pre_post_req` handles requests not pre-mapped by the core; incorrect cookie handling can leak DMA mappings.

## Test Signals

Tests should cover GX and AXG compatibles, clock tree registration and rate changes, DDR and non-DDR timing, descriptor-chain and bounce-buffer paths, DRAM access quirk with aligned and rejected unaligned SGs, SBC/main/stop sequencing, SDIO IRQ disable/ack/reenable, tuning success/failure windows, regulator voltage switch, card busy reads, GPIO card-detect IRQs, and timeout/CRC error recovery with descriptor stop polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-gx-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc-clkc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc-clkc.c

## Purpose

`meson-mx-sdhc-clkc.c` registers the clock controller embedded in the older Amlogic Meson MX SDHC block. It exposes a mux, divider, and four gate clocks derived from `MESON_SDHC_CLKC` so the SDHC host driver can use normal Linux clock APIs for module, TX, RX, and SD clocks.

## Important APIs, Types, And Functions

- `struct meson_mx_sdhc_clkc` stores clock framework objects: source mux, divider, and four gates.
- `meson_mx_sdhc_src_sel_parents` names four firmware clock inputs: `clkin0` through `clkin3`.
- `meson_mx_sdhc_div_table` lists hardware divider encodings, including non-linear divisors from 6 through 4096.
- `meson_mx_sdhc_clk_hw_register()` builds a named `clk_init_data` using `<dev_name>#<suffix>` and registers one clock hardware object with `devm_clk_hw_register()`.
- `meson_mx_sdhc_gate_clk_hw_register()` registers a gate whose parent is another `clk_hw` and stores an acquired `struct clk *` into a provided `clk_bulk_data` slot.
- `meson_mx_sdhc_register_clkc()` is the exported local API used by `meson-mx-sdhc-mmc.c`; it allocates state, registers mux/divider/gates against the SDHC MMIO base, and fills the four bulk clock slots.

## Control Flow And State

Registration is linear: allocate `clkc_data`, bind the mux to bits 17:16 of `MESON_SDHC_CLKC`, bind the divider to bits 11:0 with the divider table and mux parent, then register gate clocks on bits 15, 14, 13, and 12. The gate registration stores clocks in bulk indices 0 through 3, which the host driver later bulk-enables/disables. State is devm-managed and persists for the device lifetime.

## Dependencies And Integration Points

The file depends on the Linux clock framework, platform device/device helpers, and `meson-mx-sdhc.h` register definitions. Its sole external integration is `meson_mx_sdhc_register_clkc()`, which expects a mapped SDHC base address and a `clk_bulk_data` array sized by the caller.

## Risks And Edge Cases

- Clock names are limited to 32 bytes in a stack buffer; extremely long `dev_name()` values may be truncated.
- Bulk clock index meanings are positional and must match the host driver's expectations. The host uses `bulk_clks[1]` as `sd_clk`.
- The divider table is sparse and hardware-specific; unsupported rates depend on clock framework rounding.
- All clocks use `CLK_SET_RATE_PARENT`, so rate changes can propagate to parent clocks.

## Test Signals

Validation should confirm all five clock hardware nodes register, `clk_bulk_prepare_enable()` works for the four gates, the divider rounds expected SD rates, parent firmware clock names resolve from DT, gate bits toggle the expected `MESON_SDHC_CLKC` bits, and probe defers cleanly if parent clocks are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc-clkc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc-mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc-mmc.c

## Purpose

`meson-mx-sdhc-mmc.c` implements the Amlogic Meson8/Meson8b/Meson8m2 SDHC host controller driver. It uses the register definitions and clock-controller registration in the companion files, supports DMA-based transfers, platform-specific PDMA/FIFO quirks, tuning, regulators, and standard MMC host operations.

## Important APIs, Types, And Functions

- `struct meson_mx_sdhc_data` provides variant hooks for hardware init, PDMA setup, optional pre-send wait, and whether hardware flushes all commands.
- `struct meson_mx_sdhc_host` stores the MMC host, active request/command, sticky setup error, regmap, pclk, registered SD clock and bulk gates, and platform data.
- `meson_mx_sdhc_reset()`, `meson_mx_sdhc_clear_fifo()`, and `meson_mx_sdhc_wait_cmd_ready()` handle controller reset, FIFO cleanup, and command idle polling.
- `meson_mx_sdhc_start_cmd()` builds SEND/ICTL/CTRL/ADDR state for command and data transfers, enables relevant interrupts, waits for readiness, applies PDMA setup, and starts the command.
- `meson_mx_sdhc_set_clk()` toggles bulk clocks and programs SD clock rate plus default RX phase.
- `meson_mx_sdhc_set_ios()` handles vmmc OCR, clock, and bus width programming.
- `meson_mx_sdhc_map_dma()` maps request SGs before command start.
- `meson_mx_sdhc_execute_tuning()` scans RX clock phase values and picks the midpoint of the best all-pass window.
- `meson_mx_sdhc_irq()` records command/data CRC/timeout/FIFO errors and wakes the thread; `meson_mx_sdhc_irq_thread()` performs manual FIFO flush/read response/unmap/bytes accounting/reset/finish.
- Variant hooks include `meson_mx_sdhc_init_hw_meson8()`, `meson_mx_sdhc_set_pdma_meson8()`, `meson_mx_sdhc_wait_before_send_meson8()`, `meson_mx_sdhc_init_hw_meson8m2()`, and `meson_mx_sdhc_set_pdma_meson8m2()`.

## Control Flow And State

Probe maps registers, initializes regmap, enables `pclk`, resets and initializes hardware, registers the embedded clock tree, sets MMC limits/caps, requests a threaded IRQ, and adds the host. Requests first reuse any sticky `host->error` from setup; if clean, data SGs are mapped and `host->mrq` is set. The command start path programs data length, response flags, manual stop for multi-block SDIO CMD53, interrupt enables, argument, pack length, DMA address, readiness waits, platform PDMA configuration, and finally the SEND register.

The hard IRQ reads enabled and pending interrupt state, assigns command/data errors, and wakes the thread for all recognized events. The threaded IRQ optionally performs software RX FIFO flush for Meson8 reads, unmaps DMA, sets `bytes_xfered`, waits for command ready, reads short or long responses via the PDMA response window, resets on serious command errors, clears FIFOs after data, disables/masks IRQs, clears active pointers, and completes the request.

Clock state is managed through four bulk gates registered by `meson_mx_sdhc_register_clkc()`. `host->bulk_clks_enabled` prevents duplicate enables/disables. RX tuning state persists in `MESON_SDHC_CLK2`.

## Dependencies And Integration Points

The driver depends on platform/OF match data, regmap, Linux clocks, DMA mapping, threaded IRQs, regulators, GPIO card detect/write protect, MMC tuning helpers, and companion `meson-mx-sdhc.h`/`meson-mx-sdhc-clkc.c`. Compatibles select Meson8/8b or Meson8m2 behavior.

## Risks And Edge Cases

- `host->error` is sticky; failures in `set_ios` or clock setup cause later requests to fail until overwritten by a successful path.
- `meson_mx_sdhc_map_dma()` ignores the returned mapped segment count and assumes `sg_dma_address(cmd->data->sg)` is enough, matching `mmc->max_segs` defaults but worth preserving.
- Manual stop is set only for multi-block SDIO CMD53 based on vendor-driver behavior.
- Meson8 read flush behavior is subtle: the manual flush value depends on prior state and is required to avoid garbage SCR/status data.
- Long-response reads use PDMA response index programming; wrong index order would corrupt CID/CSD responses.
- Tuning loops through `curr_phase <= div`, so divider-derived phase range matters.

## Test Signals

Validation should cover all compatibles, pclk and bulk clock enable/disable, clock rate and RX phase programming, request error propagation from sticky setup errors, DMA map/unmap, reads and writes, multi-block SDIO CMD53 manual stop, Meson8 software flush, Meson8m2 hardware flush, response CRC/timeouts, FIFO error interrupts, long response ordering, tuning windows, card busy, regulator power-off/up, and remove-time clock shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc.h

## Purpose

`meson-mx-sdhc.h` is the shared register-definition header for the Meson MX SDHC host driver and its embedded clock-controller helper. It centralizes offsets, bitfields, and the clock registration prototype used by `meson-mx-sdhc-mmc.c` and `meson-mx-sdhc-clkc.c`.

## Important APIs, Types, And Functions

- Register offsets cover command argument/send/control/status/clock/address/PDMA/misc/data/interrupt/reset/enhancement/phase registers from `MESON_SDHC_ARGU` through `MESON_SDHC_CLK2`.
- Bitfield macros use `BIT()` and `GENMASK()` for SEND command index/response/data flags, CTRL data type/DDR/pack length/timeouts/endian/IRQ mode, STAT FIFO counts and line state, CLKC divider/power bits, PDMA mode/burst/FIFO thresholds/manual flush, MISC CRC patterns/manual stop, ICTL/ISTA interrupt bits, SRST reset bits, ENHC SoC-specific enhancements, and CLK2 phase fields.
- `struct clk_bulk_data` is forward-declared to avoid including the full clock header in users.
- `meson_mx_sdhc_register_clkc()` is declared as the clock-controller registration function.

## Control Flow And State

There is no executable logic in this header. It defines the hardware state layout that the SDHC host driver mutates during probe, request start, IRQ handling, tuning, FIFO flush, reset, and clock programming. The paired C files rely on these definitions for source-tree-aligned hardware access.

## Dependencies And Integration Points

The header depends on `linux/bitfield.h` for bitfield helpers. It integrates the Meson MX SDHC MMC host and clock-controller helper by sharing the `MESON_SDHC_CLKC` layout and the `meson_mx_sdhc_register_clkc()` declaration.

## Risks And Edge Cases

- Some register bits are SoC-specific but share offsets, especially ENHC fields for Meson6 versus Meson8m2. Callers must use the right platform hook.
- ICTL and ISTA definitions mirror each other; using the wrong register for enable versus status/ack would break IRQ handling.
- Manual FIFO flush and manual stop fields are used for hardware workarounds in the driver and are easy to regress if renamed or altered.

## Test Signals

Signals are indirect: successful compilation of both companion files, correct clock gate/divider register programming, expected interrupt enable/status masks, FIFO flush behavior, manual stop behavior, and tuning phase writes through `MESON_SDHC_CLK2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdio.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdio.c

## Purpose

`meson-mx-sdio.c` implements an older Amlogic Meson6/Meson8/Meson8b SDIO/MMC host controller driver. It supports a controller node with child `mmc-slot` devices, one active slot, DMA-mapped transfers, command timeout handling, response decoding, and an internally registered divider clock.

## Important APIs, Types, And Functions

- Register macros define SDIO argument, send, configuration, IRQ status/control, multi-slot control, DMA address, and extended data-length registers.
- `struct meson_mx_mmc_host_clkc` stores a fixed divide-by-2 clock and a configurable divider clock.
- `struct meson_mx_mmc_host` stores controller device, cfg divider clock, regmap, IRQ/spinlock, command timeout timer, slot id, MMC host, active request/command, and sticky setup error.
- `meson_mx_mmc_start_cmd()` builds SEND/EXT values, chooses response bit count, busy checking, repeated package count, data direction, slot selection, interrupt enable/ack, argument, and timeout timer.
- `meson_mx_mmc_request()` maps DMA, records the request, writes the data DMA address, and starts SBC or main command.
- `meson_mx_mmc_read_response()` reads short and long responses by programming response read index fields.
- `meson_mx_mmc_process_cmd_irq()`, `meson_mx_mmc_irq()`, and `meson_mx_mmc_irq_thread()` validate CRC bits, ack interrupts, unmap DMA, set bytes transferred, chain next command, and complete requests.
- `meson_mx_mmc_timeout()` disables command interrupts, records timeout state, and completes the request if the IRQ did not already do it.
- `meson_mx_mmc_slot_pdev()` creates the first `mmc-slot` child platform device and warns about unsupported additional slots.
- `meson_mx_mmc_register_clk()` registers a fixed-div2 clock and configurable divider backed by `MESON_MX_SDIO_CONF`.
- `meson_mx_mmc_probe()` maps resources, creates the slot child, allocates the host on the slot device, initializes regmap/IRQ/clock/config, resets hardware, and adds the host.

## Control Flow And State

The controller probe creates a child slot platform device and allocates the MMC host under that slot. It initializes the SDIO configuration register with argument width, endian, write timing, and CRC status patterns, soft-resets the controller, parses the slot, and adds the host.

Requests persist in `host->mrq` and `host->cmd`. Data SGs must be 32-bit aligned and are DMA-mapped before start. If an SBC exists, it is sent first; otherwise the main command is sent. Command start selects the slot, enables command-done IRQ, clears pending command IRQ, writes argument and transfer size, starts the command, and arms a per-command timer. The hard IRQ reads status and SEND configuration, processes command completion if present, and acks all pending IRQs. The thread deletes the timer, unmaps data, sets bytes transferred, and either starts the next command (main after CMD23 or stop after multi-block) or completes the request.

The timeout path disables command interrupts under `irq_lock`, checks if another path already cleared `host->cmd`, logs status, sets `-ETIMEDOUT`, soft-resets during request completion, and completes the request.

## Dependencies And Integration Points

The driver depends on platform/OF infrastructure, child node creation through `of_platform_device_create()`, regmap, clocks, DMA mapping, timers, threaded IRQs, regulators, GPIO CD/WP helpers, and MMC core parsing. It matches `"amlogic,meson8-sdio"` and `"amlogic,meson8b-sdio"`.

## Risks And Edge Cases

- Multiple hardware slots are not really supported; only the first `mmc-slot` child is registered.
- `host->error` is sticky after `set_ios` or mapping failures and can fail later requests until reset by a successful path.
- Only the first SG entry is alignment-checked before mapping, while the mapped request may contain more entries.
- Timeout and IRQ paths coordinate via `host->cmd` and interrupt disable; races are handled defensively but remain critical.
- The driver sets `bytes_xfered` to the full request size whenever data command IRQ completes, relying on CRC/status validation.
- Long response bit shifting is custom and must remain aligned with hardware response FIFO semantics.

## Test Signals

Validation should cover one-slot DT probing, warning on multiple slots, clock divider registration/rate changes, 1-bit and 4-bit bus modes, regulator OCR changes, aligned DMA reads/writes, rejection of unaligned first SG, command timeout timer, duplicate command IRQ tolerance, CRC error detection for response and data, SBC/main/stop chaining, card detect/write protect GPIOs, and remove-time timer/clock/device cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.c

## Purpose

`mmc_hsq.c` implements MMC host software queue support using the MMC CQE interface. It allows hosts without hardware command queueing to accept tagged CQE requests and pump them serially to normal `mmc_host_ops->request` or `request_atomic`, with a small adjustable queue depth.

## Important APIs, Types, And Functions

- `mmc_hsq_retry_handler()` retries a request in process context after `request_atomic()` reports `-EBUSY`.
- `mmc_hsq_modify_threshold()` changes `mmc->hsq_depth` from normal depth 2 to performance depth 5 when it observes two queued 4 KiB write requests.
- `mmc_hsq_pump_requests()` selects `next_tag`, sets `hsq->mrq`, decrements queue count, and submits to the underlying host.
- `mmc_hsq_update_next_tag()` advances the linked tag queue or invalidates head/tail when empty.
- `mmc_hsq_finalize_request()` is exported for host drivers to complete the active software-queued request; it validates the active request, clears the slot, calls `mmc_cqe_request_done()`, and pumps the next request.
- CQE callbacks implement recovery halt/resume, queueing, post_req forwarding, wait-for-idle, enable, and disable.
- `mmc_hsq_init()` allocates slots, assigns `mmc->cqe_ops`, stores `cqe_private`, initializes tags, work, spinlock, and wait queue.
- `mmc_hsq_suspend()`/`mmc_hsq_resume()` disable and enable the queue for PM.

## Control Flow And State

The CQE core calls `mmc_hsq_request()` with a tagged request. The driver stores it in `slot[tag]`, links the tag at the queue tail using `tag_slot`, increments `qcnt`, and tries to pump. Pumping is serialized by `hsq->mrq`: only one request is submitted to the hardware host at a time. On completion the host driver calls `mmc_hsq_finalize_request()`, which clears the active slot, completes to the CQE core, clears `hsq->mrq`, advances `next_tag`, wakes waiters if idle, and pumps the next queued request unless recovery is halted.

Recovery state is controlled by `recovery_halt`. While set, new CQE queueing returns `-EBUSY`, pumping stops, and wait-for-idle reports `-EBUSY`. Disable waits up to 500 ms for idle before setting `enabled = false`.

## Dependencies And Integration Points

The file depends on MMC card/host core and `mmc_hsq.h`. Host drivers integrate by embedding `struct mmc_hsq`, calling `mmc_hsq_init()`, exposing CQE support to the core, and calling `mmc_hsq_finalize_request()` when their underlying request completes. It also forwards `post_req` to underlying `mmc->ops->post_req` when available.

## Risks And Edge Cases

- `mmc_hsq_pump_requests()` assumes `next_tag` indexes a valid queued slot whenever `qcnt` is nonzero; tag linking bugs would dereference an invalid slot.
- The performance-depth heuristic is very specific to two queued 4 KiB writes and may not generalize.
- `request_atomic()` fallback schedules work only for `-EBUSY`; other errors are warned but left for the host driver to handle.
- Disable timeout only warns and returns without forcibly clearing enabled state if the queue cannot stop.
- The queue serializes hardware execution despite accepting CQE-style tags, so it improves software queueing but not true parallel command execution.

## Test Signals

Tests should cover CQE enable/disable, queueing multiple tagged requests, tag order preservation, finalize of the active request, reject/fallback when disabled or recovery halted, retry work on `request_atomic == -EBUSY`, wait-for-idle wakeups, suspend/resume, post_req forwarding, and depth changes under repeated 4 KiB writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.h

## Purpose

`mmc_hsq.h` is the private/public header for MMC host software queue support. It defines queue dimensions, queue state structures, and exported helper prototypes used by host drivers that want CQE-style software queueing without a hardware CQE engine.

## Important APIs, Types, And Functions

- `HSQ_NUM_SLOTS` is 64, matching the supported tag array size.
- `HSQ_INVALID_TAG` is the sentinel value equal to `HSQ_NUM_SLOTS`.
- `HSQ_NORMAL_DEPTH` is 2, chosen to limit latency.
- `HSQ_PERFORMANCE_DEPTH` is 5, used by the implementation's 4 KiB random-write heuristic.
- `struct hsq_slot` stores one `struct mmc_request *` per tag.
- `struct mmc_hsq` stores the associated MMC host, active request, wait queue, slot array, lock, retry work, head/tail/tag link state, queue count, and booleans for enabled, waiting-for-idle, and recovery halt.
- Prototypes: `mmc_hsq_init`, `mmc_hsq_suspend`, `mmc_hsq_resume`, and `mmc_hsq_finalize_request`.

## Control Flow And State

The header defines the persistent state that `mmc_hsq.c` mutates. `slot[]` maps tags to requests; `tag_slot[]` acts as a linked list of queued tags; `next_tag` and `tail_tag` define the queue; `mrq` is the single currently submitted hardware request; and the boolean flags coordinate enable/disable and recovery behavior.

## Dependencies And Integration Points

This header relies on MMC core types being visible to users. It is included by `mmc_hsq.c` and host drivers embedding `struct mmc_hsq`. The finalization API is the key integration point for underlying host-completion paths.

## Risks And Edge Cases

- Queue size is fixed at 64; host tags must be within that range.
- `HSQ_INVALID_TAG` is a valid array length but invalid index; callers must never index with it.
- The header exposes internal structure layout, so host drivers can embed but should not mutate fields directly outside the helper API.

## Test Signals

Signals are mostly compile-time and integration-level: embedded `struct mmc_hsq` size/layout, successful `mmc_hsq_init()`, valid CQE callback registration, and finalization from a host driver with request tags in the 0-63 range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_spi.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_spi.c

## Purpose

`mmc_spi.c` implements an MMC host driver that speaks the SD/MMC SPI transport over a generic Linux SPI controller. It maps MMC requests into SPI command frames, response parsing, block tokens, CRC handling, chip-select management, optional platform power/card-detect glue, and MMC host registration for `"mmc-spi-slot"` devices.

## Important APIs, Types, And Functions

- Protocol constants define SPI data-response codes, data tokens, 512-byte block size, busy/init timeouts, and maximum blocks per request.
- `struct scratch` holds per-command status bytes, a data token, and CRC storage.
- `struct mmc_spi_host` stores the MMC host, SPI device, power state, platform data, reusable SPI transfers/messages for data and status, scratch buffer, and an all-ones transmit buffer.
- `mmc_spi_readbytes()`, `mmc_spi_skip()`, `mmc_spi_wait_unbusy()`, and `mmc_spi_readtoken()` implement low-level polling while keeping chip select active.
- `mmc_spi_response_get()` parses SPI R1/R1B/R2/R3/R4/R5/R7-style responses, including bit-shifted response recovery and busy waiting.
- `mmc_spi_command_send()` formats a 6-byte command plus CRC7, performs a full-duplex SPI transfer, and delegates response parsing.
- `mmc_spi_setup_data_message()` builds reusable SPI messages for read/write block bodies, CRCs, data tokens, and early write status.
- `mmc_spi_writeblock()` sends one data block, validates the data-response token bit pattern, advances TX buffer, and waits until not busy.
- `mmc_spi_readblock()` scans for a data token, handles bit-shifted data streams, optionally validates CRC16, and advances RX buffer.
- `mmc_spi_data_do()` iterates scatterlist entries and 512-byte blocks, maps pages with `kmap()`, transfers each block, updates `bytes_xfered`, flushes read pages, and sends multi-block write stop token.
- `mmc_spi_request()` locks the SPI bus, sends command/data/stop, retries CRC data errors up to five times using a synthetic STOP_TRANSMISSION, releases the bus, and completes the MMC request.
- `mmc_spi_set_ios()` handles platform power switching, initialization clocks with chip-select high, power-off line grounding, and SPI clock updates.
- `mmc_spi_probe()` validates full-duplex SPI, configures mode/bits, allocates buffers/host, reads platform data/OCR/caps, sets MMC limits/caps, initializes card-detect glue/GPIOs, and adds the host.

## Control Flow And State

MMC requests are serialized by `spi_bus_lock()`. The driver sends the command with chip select left active if data follows. Data transfers use SPI block tokens rather than native controller DMA descriptors: for each SG segment, the driver maps the page, points the reusable SPI transfer at the SG data, and loops block by block through `mmc_spi_writeblock()` or `mmc_spi_readblock()`. Multi-block writes end with a `SPI_TOKEN_STOP_TRAN` sequence and busy wait. If data had a CRC error, the request path sends STOP_TRANSMISSION, clears the data error, and retries the full command up to five times.

Response state is stored in `cmd->resp[0]` for SPI R1/R2-style status and `cmd->resp[1]` for four-byte SPI responses. The scratch buffer is reused for command status, data token, CRC, and busy polling. Power state persists in `host->power_mode`, and `mmc_spi_set_ios()` only performs platform power or init sequence when the mode changes.

Probe state includes an allocated all-ones block buffer used as TX filler for reads and busy polling, plus platform data callbacks for init/exit/setpower. Remove disables future detect callbacks, removes the host, frees buffers, restores `spi->max_speed_hz`, and releases platform data.

## Dependencies And Integration Points

The driver depends on Linux SPI core full-duplex transfer support, MMC core SPI response flags, CRC7 and CRC-ITU-T helpers, scatterlists, highmem `kmap/kunmap`, GPIO slot helpers, and optional `linux/spi/mmc_spi.h` platform data. It matches both SPI ID and OF compatible `"mmc-spi-slot"`.

## Risks And Edge Cases

- The driver requires full-duplex SPI controllers and warns when the controller cannot go down to 400 kHz.
- Chip-select behavior is critical. The comments call out dependence on controllers honoring `cs_change` and lack of safe shared-bus semantics.
- Response and data tokens may be bit-shifted by real cards; the driver contains custom recovery paths that are easy to regress.
- Multi-block write stop token handling is not the same as MMC command STOP_TRANSMISSION and must preserve chip select and busy polling.
- Data transfers use `kmap()` and do not allow highmem-style asynchronous DMA ownership; each block is transferred synchronously.
- Power-off mode temporarily rewrites SPI mode and clocks a null byte to ground card inputs; failure paths only log debug messages.
- Card detect GPIOs are requested after `mmc_add_host()`, so deferred GPIO probe removes the host and unwinds buffers.

## Test Signals

Validation should include probe rejection on half-duplex controllers, SPI mode 0 and platform-selected mode 3, command-only requests, all SPI response types, bit-shifted response/data token recovery, single and multi-block reads/writes, CRC enabled/disabled operation, CRC retry loop, multi-block write stop token, card-detect IRQ/GPIO and polling fallback, write-protect GPIO, platform power callbacks and init/exit, speed changes from `set_ios`, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_spi.c -->
