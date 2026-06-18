# Research: subset-b-004273

Grouped research for MMC host-controller sources under `sources/distributed-fs/ceph-client/drivers/mmc/host`. Each section is source-tree-aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mxcmmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/mxcmmc.c

## Purpose
`mxcmmc.c` is the platform driver for the Freescale i.MX21/i.MX31 and MPC512x SDHC/MMCI block. It registers the `mxc-mmc` MMC host, maps controller registers, handles card detect and SDIO IRQs, and runs either DMA or PIO data transfers for MMC core requests.

## Important APIs, Types, And Functions
The main state carrier is `struct mxcmci_host`, which binds the `mmc_host`, MMIO base, clocks, DMA channel/descriptor, current `mmc_request`/`mmc_command`/`mmc_data`, interrupt mask, watchdog timer, and SoC type. `mxcmci_probe()` allocates and initializes the host, parses DT/platform data, enables clocks, validates the hardware revision, requests DMA and IRQ resources, and calls `mmc_add_host()`. The MMC ops are `mxcmci_request()`, `mxcmci_set_ios()`, `mxcmci_get_ro()`, `mxcmci_enable_sdio_irq()`, and `mxcmci_init_card()`. Transfer helpers include `mxcmci_setup_data()`, `mxcmci_start_cmd()`, `mxcmci_cmd_done()`, `mxcmci_data_done()`, `mxcmci_transfer_data()`, and `mxcmci_watchdog()`.

## Control Flow
Requests enter at `mxcmci_request()`, set `host->req`, optionally prepare data, then write command argument/opcode/control fields. Command completion is reported by `mxcmci_irq()` on `STATUS_END_CMD_RESP`, which reads the response and either finishes command-only requests or schedules PIO data work. DMA reads finish through `mxcmci_dma_callback()`, DMA writes through `STATUS_WRITE_OP_DONE`, and PIO transfers run in `mxcmci_datawork()` outside interrupt context. Data completion may start a stop command or call `mmc_request_done()`.

## State And Persistence
Runtime state is volatile kernel driver state: clocks, `cmdat`, `power_mode`, SDIO enable, DMA fallback state, active request pointers, and a watchdog timer. No durable persistence exists. MPC512x endianness is handled by custom register accessors and buffer swapping.

## Dependencies And Integration Points
The driver integrates with the MMC core, platform driver core, device tree compatibles, legacy `imxmmc_platform_data`, regulators, GPIO slot helpers, DMAengine/imx-dma, clocks, IRQ handling, and PM sleep callbacks.

## Risks And Test Signals
Risk concentrates in mixed DMA/PIO fallback, timeout cleanup, DMA unmap ordering, MPC512x byte swapping, and the i.MX31 SDIO four-bit quirk. Useful signals include boot probe logs, `mmc_add_host()` success, card insertion/removal interrupts, read/write CRC and timeout paths, SDIO IRQ delivery, DMA unavailable fallback, suspend/resume clock restoration, and multi-block SDIO testing on i.MX31.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mxcmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mxs-mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/mxs-mmc.c

## Purpose
`mxs-mmc.c` drives the Freescale MXS SSP-based MMC controller for i.MX23/i.MX28 platforms. It uses the MXS SSP block and DMAengine to submit command descriptor words and data scatterlists, supports polling or GPIO/native card detection, and exposes SD/MMC/SDIO-capable host operations.

## Important APIs, Types, And Functions
`struct mxs_mmc_host` embeds `struct mxs_ssp` and tracks the active MMC request, command, data, bus width, SDIO IRQ enable, and broken-card-detect flag. `mxs_mmc_probe()` maps registers, obtains the clock/regulator/DMA channel, resets the SSP, sets MMC caps and transfer limits, requests the IRQ, and registers the host. Request processing is divided by command type across `mxs_mmc_bc()`, `mxs_mmc_ac()`, `mxs_mmc_adtc()`, and `mxs_mmc_start_cmd()`. `mxs_mmc_prep_dma()` prepares both command PIO-word descriptors and data descriptors. IRQ and completion paths are `mxs_mmc_irq_handler()`, `mxs_mmc_dma_irq_callback()`, and `mxs_mmc_request_done()`.

## Control Flow
`mxs_mmc_request()` stores the request and starts CMD23 (`mrq->sbc`) first if present; otherwise it starts the main command. Command setup writes SSP PIO words and submits DMA descriptors. ADTC commands first submit command words, then attach the data SG DMA descriptor. The DMA callback reads responses, unmaps data, advances from CMD23 to the main command, optionally sends a stop command, and finally calls `mmc_request_done()`. The hardware IRQ mostly records error status and SDIO IRQ events; the DMA callback is the normal completion edge.

## State And Persistence
All state is transient in `mxs_mmc_host` and the embedded `mxs_ssp`. The driver remembers current bus width and SDIO IRQ enable across resets so `mxs_mmc_reset()` reprograms IRQ-check bits. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on MXS SSP register definitions/helpers, `stmp_reset_block()`, DMAengine, the MMC core, OF compatibles, regulator and clock frameworks, GPIO card-detect helpers, and PM sleep hooks.

## Risks And Test Signals
Key risks are descriptor sequencing, mapping/unmapping on descriptor preparation failure, timeout tick calculation, SDIO IRQ interaction with continuous clocking, and card-detect polarity/polling behavior. Test signals include successful i.MX23/i.MX28 probe, DMA channel acquisition, command-only and data command completion, CMD23 flows, stop command issuance, SDIO interrupt signaling, broken-CD behavior, and suspend/resume clock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mxs-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/of_mmc_spi.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/of_mmc_spi.c

## Purpose
`of_mmc_spi.c` is a small OpenFirmware/fwnode adapter for the generic MMC-over-SPI driver. It builds `struct mmc_spi_platform_data` from firmware properties when the SPI device has no explicit platform data.

## Important APIs, Types, And Functions
`struct of_mmc_spi` wraps `mmc_spi_platform_data` and a detect IRQ. `mmc_spi_get_pdata()` allocates the wrapper, parses voltage OCR with `mmc_of_parse_voltage()`, configures card-detect IRQ callbacks or polling, reads high-speed capability properties, and installs `dev->platform_data`. `mmc_spi_put_pdata()` frees firmware-created platform data. `of_mmc_spi_init()` and `of_mmc_spi_exit()` request/free the threaded detect IRQ.

## Control Flow
The SPI MMC driver calls `mmc_spi_get_pdata()` during setup. If platform data already exists or the device has no firmware node, the existing pointer is returned. Otherwise firmware-derived data is allocated, populated, and stored on the device. On teardown, `mmc_spi_put_pdata()` frees only firmware-generated data.

## State And Persistence
The only stored state is heap-allocated platform data attached to `dev->platform_data`. It persists for the SPI device lifetime and is not durable.

## Dependencies And Integration Points
This file integrates firmware property parsing, OF IRQ/SPI device information, MMC core voltage parsing, and the generic `mmc_spi` platform-data contract. Its exported symbols are consumed by the MMC SPI host driver.

## Risks And Test Signals
Risks are mostly lifecycle-related: freeing only data owned by this adapter, avoiding misuse when real platform data exists, and ensuring `dev_get_drvdata()` already provides the `mmc_host` before voltage parsing. Test signals include DT SPI MMC probe, high-speed property propagation, IRQ versus polling detect selection, and clean remove without leaks or double frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/of_mmc_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/omap.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/omap.c

## Purpose
`omap.c` is the legacy OMAP MMC host driver for OMAP1/OMAP2-era controllers. It supports multiple logical slots on one controller, slot power and cover switches, PIO or DMA transfers, command abort timers, and platform-data-based board integration.

## Important APIs, Types, And Functions
`struct mmc_omap_host` owns controller state: current request/command/data, clocks, DMA channels, IRQ, MMIO base, slot arbitration, workqueue, timers, and feature flags. `struct mmc_omap_slot` represents each MMC slot and stores its `mmc_host`, power GPIOs, cover GPIO, saved CON register, and queued request. Main functions are `mmc_omap_probe()`, `mmc_omap_new_slot()`, `mmc_omap_request()`, `mmc_omap_set_ios()`, `mmc_omap_prepare_data()`, `mmc_omap_start_command()`, `mmc_omap_irq()`, `mmc_omap_cmd_done()`, `mmc_omap_xfer_done()`, and cover-event helpers including exported `omap_mmc_notify_cover_event()`.

## Control Flow
Requests are serialized by `slot_lock`. If another slot owns the controller, the request is queued on that slot; otherwise `mmc_omap_select_slot()` switches hardware state and starts it. Data setup chooses DMA when all SG lengths are block-aligned and channels/configuration are available; otherwise it initializes an atomic SG iterator for IRQ-driven PIO. IRQ processing drains FIFO signals, handles command/data CRC and timeout errors, detects end-of-command and end-of-data, then coordinates DMA completion (`brs_received` and `dma_done`) before finishing, sending stop, or aborting.

## State And Persistence
State is in memory only. Slot register settings, power mode, selected slot, queued requests, DMA progress flags, cover polling timers, and delayed clock-off state are retained while the driver is bound. There is no persistent state.

## Dependencies And Integration Points
The driver depends on `omap_mmc_platform_data`, board callbacks, GPIO descriptors, clocks, DMAengine, MMC core, workqueues, timers, sysfs attributes, and platform IRQ/resource management.

## Risks And Test Signals
Risks include multi-slot arbitration, request queuing under locks, DMA/PIO race handling, abort work disabling/enabling IRQs, cover polling behavior, and hardware-specific register shift differences. Test signals include one-slot and multi-slot enumeration, PIO fallback, DMA completion ordering, command timeout aborts, cover switch sysfs updates, stop command paths, card removal during transfer, and cleanup of timers/workqueue on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/omap_hsmmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/omap_hsmmc.c

## Purpose
`omap_hsmmc.c` drives the OMAP2430/3430 and related TI high-speed MMC controller family. It provides DMA-backed request execution, regulator and pbias power handling, voltage switching, runtime PM, SDIO wake IRQ support, debugfs register visibility, and DT/platform-data compatibility.

## Important APIs, Types, And Functions
`struct omap_hsmmc_host` tracks the MMC host, active request/command/data, clocks, regulators, IRQ and wake IRQ, DMA channels, saved register context, power mode, flags such as `AUTO_CMD23`, and pre-request DMA cookie state. Probe path `omap_hsmmc_probe()` parses OF/platform data, maps registers, enables runtime PM, configures bus power, requests DMA/IRQ resources, installs wake IRQ if possible, and registers the host. Core ops include `omap_hsmmc_request()`, `omap_hsmmc_set_ios()`, `omap_hsmmc_enable_sdio_irq()`, `omap_hsmmc_pre_req()`, and `omap_hsmmc_post_req()`.

## Control Flow
Requests prepare DMA in `omap_hsmmc_prepare_data()` and `omap_hsmmc_setup_dma_transfer()`. If CMD23 is present and hardware auto-CMD23 is unavailable, the SBC is issued first; its command-complete path starts DMA and the real command. IRQ handling loops over `STAT`, delegates to `omap_hsmmc_do_irq()`, maps error bits to command/data errors, resets command/data FSMs on faults, and completes commands/transfers. DMA completion clears `dma_ch`, unmaps if needed, and may finish a request that already saw transfer complete.

## State And Persistence
Runtime state includes active request flags, saved `CON/HCTL/SYSCTL/CAPA` context, `power_mode`, regulator enable booleans, DMA cookie cache, SDIO IRQ enable, and context-loss count. State is restored after runtime resume but not persisted across driver unload.

## Dependencies And Integration Points
The driver integrates MMC core, DMAengine, OF matches, legacy `hsmmc-omap` platform data, regulators (`vmmc`, `vqmmc`/`vmmc_aux`, `pbias`), pinctrl idle/default states, runtime/system PM, wake IRQ infrastructure, GPIO slot helpers, and debugfs.

## Risks And Test Signals
Risk areas include DMA completion versus transfer-complete ordering, command/data FSM reset paths, runtime suspend while SDIO IRQ is pending, voltage switch sequencing, boot regulator usecount correction, and broken-multiblock-read quirks. Test signals include DMA read/write with pre/post request, CMD23 and auto-CMD23 paths, busy-response commands without data, SDIO wake from runtime suspend, context-loss restore, regulator/pbias transitions, debugfs register reads, and erratum-driven multi-IO quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/omap_hsmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/owl-mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/owl-mmc.c

## Purpose
`owl-mmc.c` is the Actions Semi Owl SoC SD/MMC host driver. It programs Owl SDC registers, uses an external DMA channel for data, handles command and DMA completions with completions, and supports SD/MMC high-speed and DDR50-style timing without SDIO support.

## Important APIs, Types, And Functions
`struct owl_mmc_host` stores device resources, reset/clock handles, completions, lock, DMA channel/configuration, MMC host, and active request/command/data. `owl_mmc_probe()` maps registers, obtains clock/reset/DMA/IRQ, initializes host limits and caps, parses OF MMC properties, and registers the host. Main ops are `owl_mmc_request()`, `owl_mmc_set_ios()`, `owl_mmc_start_signal_voltage_switch()`, `mmc_gpio_get_ro()`, and `mmc_gpio_get_cd()`. Helpers include `owl_mmc_send_cmd()`, `owl_mmc_prepare_data()`, `owl_irq_handler()`, `owl_mmc_dma_complete()`, and clock/bus-width/power helpers.

## Control Flow
For data requests, `owl_mmc_request()` maps the SG list, configures DMA, submits it, sends the command, waits for controller transfer-end completion, waits for DMA completion, optionally sends a stop command, records `bytes_xfered`, and finishes the request. Command-only requests wait inside `owl_mmc_send_cmd()`, validate response/no-response/CRC status bits, and fill response words.

## State And Persistence
The driver stores current clock rate, DDR50 mode, active request pointers, DMA direction, and completions in memory only. Controller state is reset on power-up via reset control and clock enable; no persistent state exists.

## Dependencies And Integration Points
It integrates with platform/OF probing, reset and clock frameworks, DMAengine, MMC core, GPIO card-detect/write-protect helpers, IRQ handling, and 1.8 V signal switching through an SDC pad-control bit.

## Risks And Test Signals
Risks include blocking waits in the request path, DMA unmap after preparation failures, no SDIO capability, hard-coded delay tuning by clock range, and timeout cleanup with active DMA. Test signals include probe with DMA channel, command-only responses including R2/R3, read and write DMA completion, stop-command handling, power mode transitions, DDR50 timing, voltage switch, and timeout/error status reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/owl-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.c

## Purpose
`pxamci.c` is the PXA2xx/PXA3xx Multimedia Card Interface driver. It handles a quirky controller that requires clock stopping before register access, uses DMA with a single SG segment, supports platform and DT setup, and exposes SDIO IRQ and GPIO/platform read-only/card-detect behavior.

## Important APIs, Types, And Functions
`struct pxamci_host` holds the MMC host, locks, MMIO resource, clock divisor state, command attributes, interrupt mask, power controls, active request pointers, and RX/TX DMA channels. `pxamci_probe()` initializes limits, parses OF/platform data, configures OCR and caps, maps registers, requests IRQ/DMA channels, configures GPIO/platform callbacks, and calls `mmc_add_host()`. Main ops are `pxamci_request()`, `pxamci_set_ios()`, `pxamci_get_ro()`, `pxamci_enable_sdio_irq()`, and `mmc_gpio_get_cd()`. Core helpers include `pxamci_setup_data()`, `pxamci_start_cmd()`, `pxamci_cmd_done()`, `pxamci_data_done()`, `pxamci_irq()`, and `pxamci_dma_irq()`.

## Control Flow
`pxamci_request()` stops the clock, prepares DMA for data, builds `CMDAT`, and starts the command. The IRQ handler masks `MMC_I_REG` against `MMC_I_MASK`, then handles command response and data-transfer completion. `pxamci_cmd_done()` reads the unusual response FIFO layout, maps timeout/CRC errors, enables data completion IRQ, and starts write DMA late on PXA27x erratum #91. `pxamci_data_done()` unmaps DMA, sets transferred bytes or error, then sends stop or completes the request.

## State And Persistence
Runtime state includes `clkrt`, `cmdat`, IRQ mask, power mode, detect delay, active request/data, DMA cookie and length. There is no durable storage; platform callbacks may manipulate external power or GPIO state.

## Dependencies And Integration Points
The driver uses the MMC core, DMAengine, PXA CPU detection helpers, regulator and GPIO frameworks, platform data, OF parsing, clocks, IRQs, and the register constants from `pxamci.h`.

## Risks And Test Signals
Risks include known hardware errata, single-SG DMA limitation, response parsing, clock-stop requirements, DMA error callback reentry, and mixed GPIO/platform power and write-protect definitions. Test signals include PXA25x versus PXA27x/PXA3xx caps, 26 MHz high-speed operation, SDIO IRQ, DMA read/write including write-late erratum path, stop command handling, GPIO CD/WP, and remove-time DMA termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.h

## Purpose
`pxamci.h` defines the PXA MCI register offsets and bit masks consumed by `pxamci.c`. It is a hardware contract header, not an independent driver.

## Important APIs, Types, And Functions
The header exposes register offsets such as `MMC_STRPCL`, `MMC_STAT`, `MMC_CLKRT`, `MMC_CMDAT`, `MMC_I_MASK`, `MMC_I_REG`, `MMC_CMD`, argument/response registers, and FIFO ports. It defines command/power/control bits such as `STOP_CLOCK`, `START_CLOCK`, `CMDAT_DMAEN`, `CMDAT_INIT`, `CMDAT_DATAEN`, `CMDAT_WRITE`, and response type encodings. It also defines status and interrupt bits for command response, program done, data transfer done, FIFO service, SDIO, and errors.

## Control Flow
There is no executable control flow. `pxamci.c` uses these constants to stop/start the clock, configure command attributes, unmask interrupts, read status, and access FIFOs.

## State And Persistence
The header stores no state. Its conditional `MMC_I_MASK_ALL` value depends on build configuration for PXA27x/PXA3xx versus older PXA targets, shaping the runtime driver's default interrupt mask.

## Dependencies And Integration Points
The sole integration point is inclusion by the PXA MCI driver. The constants mirror the controller programming model and must stay synchronized with the implementation's command, DMA, IRQ, and FIFO handling.

## Risks And Test Signals
Risks are incorrect bit definitions or build-conditional masks causing missed/unexpected interrupts or wrong command modes. Test signals are indirect: successful PXA command/data/SDIO operation, clock control, FIFO service, and error decoding in `pxamci.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi.h

## Purpose
`renesas_sdhi.h` is the shared private interface for the Renesas SDHI driver family. It defines SoC capability data, tuning/quirk structures, DMA-private state, the per-host private object, and exported lifecycle functions used by the DMA front-end drivers.

## Important APIs, Types, And Functions
`struct renesas_sdhi_of_data` describes TMIO flags, OCR/capabilities, DMA bus width and offsets, bus shift, SCC tuning offset/taps, block and segment limits, and SDHI flags. `struct renesas_sdhi_quirks` records HS400, tap correction, fixed-address DMA, one-RX-DMAC, and INFO1 layout quirks. `struct renesas_sdhi_dma` stores DMA end flags, bus width, DMA filter, core DMA-enable callback, completion, and work item. `struct renesas_sdhi` is the core private state containing clocks, TMIO data, DMA state, quirks, pinctrl/SCC/tuning data, reset control, TMIO host, and optional regulator device. The header declares `renesas_sdhi_probe()`, `renesas_sdhi_remove()`, `renesas_sdhi_suspend()`, and `renesas_sdhi_resume()`.

## Control Flow
There is no executable logic beyond the `host_to_priv()` container macro and `sdhi_has_quirk()` helper. Runtime flow is implemented by `renesas_sdhi_core.c` and the DMA variants using these contracts.

## State And Persistence
The structures define volatile in-kernel state for clocks, tuning decisions, DMA end coordination, card type, and regulator/reset handles. No persistent state exists.

## Dependencies And Integration Points
The header bridges the SDHI core, `tmio_mmc` core, system DMAC and internal DMAC front-ends, platform devices, DMAengine, workqueues, and MMC capabilities.

## Risks And Test Signals
Risks include ABI-like drift between the core and DMA front-ends, incorrect SoC data, and quirk fields changing semantics. Test signals are build coverage of all SDHI variants and runtime validation of tuning, DMA, suspend/resume, and voltage-switch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_core.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_core.c

## Purpose
`renesas_sdhi_core.c` implements the common Renesas SDHI host logic on top of the TMIO MMC core. It handles clock selection, SDBUF bus width, signal voltage switching, SCC tuning and HS400 adjustment, reset behavior, SDIO retune handling, a local `vqmmc` regulator, common probe/remove, and suspend/resume.

## Important APIs, Types, And Functions
Exported APIs are `renesas_sdhi_probe()`, `renesas_sdhi_remove()`, `renesas_sdhi_suspend()`, and `renesas_sdhi_resume()`. Core callbacks installed into `tmio_mmc_host` include `renesas_sdhi_clk_enable()`, `renesas_sdhi_clk_disable()`, `renesas_sdhi_set_clock()`, `renesas_sdhi_reset()`, `renesas_sdhi_write16_hook()`, `renesas_sdhi_multi_io_quirk()`, `renesas_sdhi_check_scc_error()`, and tuning hooks such as `renesas_sdhi_execute_tuning()`, `renesas_sdhi_prepare_hs400_tuning()`, and `renesas_sdhi_hs400_complete()`. Regulator ops expose SDHI voltage selection through `CTL_SD_STATUS`.

## Control Flow
Probe allocates `struct renesas_sdhi`, obtains clocks/reset/pinctrl/mux, allocates a TMIO host, applies OF/platform data and quirks, enables clocks, optionally registers a child `vqmmc` regulator, discovers version/SCC support, installs TMIO callbacks, requests IRQs, and calls `tmio_mmc_host_probe()`. Clock setting updates parent clocks, computes TMIO dividers, and toggles SCLK. Tuning initializes SCC, runs CMD19 twice per tap, selects the longest passing tap window, and configures correction. Request-time hooks can adjust HS400 calibration before status commands and request retuning on SCC errors.

## State And Persistence
Runtime state includes clock handles/rates, SCC tap bitmaps and selected tap, HS400 calibration flags, card SDIO classification, reset/regulator handles, and TMIO private data. This is volatile and restored through PM and reset paths, not persisted.

## Dependencies And Integration Points
The core depends on TMIO MMC internals, Renesas SDHI registers, clocks, resets, pinctrl, mux controls, regulators, OF/platform data, IRQs, runtime PM domains, and the DMA ops supplied by front-end drivers.

## Risks And Test Signals
Risks include clock rounding errors, SCC tap selection on marginal boards, HS400 bad-tap/calibration quirks, SDIO IRQ retune interactions, reset preserving regulator state, and version-dependent block-count/CBSY behavior. Test signals include Gen2/Gen3 probe, clock rates and actual clock reporting, voltage switch with pinctrl, SDR104/HS200/HS400 tuning, SDIO IRQ retune, local regulator operation, reset/suspend/resume, and TMIO IRQ-driven request success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_internal_dmac.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_internal_dmac.c

## Purpose
`renesas_sdhi_internal_dmac.c` is the SDHI front-end for Renesas controllers with an integrated DMAC. It supplies SoC match data and TMIO DMA operations to the common SDHI core, including internal-DMAC register programming, DMA completion coordination, pre/post mapping, and SoC-specific HS400 quirks.

## Important APIs, Types, And Functions
The file defines internal DMAC registers (`DM_CM_DTRAN_*`, `DM_CM_INFO*`, `DM_DTRAN_ADDR`), DMA cookies, global one-RX-use flag, R-Car/RZ OF data, SCC tap data, calibration tables, quirk tables, and OF match entries. DMA ops are implemented by `renesas_sdhi_internal_dmac_start_dma()`, `renesas_sdhi_internal_dmac_enable_dma()`, `renesas_sdhi_internal_dmac_abort_dma()`, `renesas_sdhi_internal_dmac_dataend_dma()`, `renesas_sdhi_internal_dmac_end_dma()`, `renesas_sdhi_internal_dmac_dma_irq()`, request/release hooks, and pre/post request hooks.

## Control Flow
Probe selects OF data/quirks, may override quirks via `soc_device_match()`, sets max DMA segment size, and calls `renesas_sdhi_probe()` with internal DMAC ops. Start maps the SG list, enforces 128-byte alignment, chooses read/write channel mode, optionally enforces the one-RX-DMAC workaround, enables DMA, writes transfer mode/address, and marks `host->dma_on`. The DMAC IRQ and TMIO DATAEND path set separate bits; only when both have occurred does workqueue completion call `tmio_mmc_do_data_irq()`.

## State And Persistence
State includes `data->host_cookie` mapping state, `dma_priv.end_flags`, `host->dma_on`, fake non-null `chan_rx/chan_tx` flags, and a global RX-in-use bit for affected SoCs. No durable state exists.

## Dependencies And Integration Points
The file integrates with Renesas SDHI core, TMIO DMA ops, MMC pre_req/post_req, system workqueues, SoC revision matching, OF matching, DMA mapping API, and internal SDHI DMAC registers.

## Risks And Test Signals
Risks include alignment fallback to PIO, global RX serialization, two-edge completion races, old INFO1 layout quirks, fixed-address mode, DMA abort reset sequencing, and fake channel pointers used as enable flags. Test signals include Gen3/RZ probe, pre-mapped request reuse, unaligned buffer PIO fallback, simultaneous channel RX workaround, DMA IRQ plus DATAEND ordering, abort on errors, HS400 quirk selection by SoC revision, and suspend/resume through common SDHI PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_internal_dmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_sys_dmac.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_sys_dmac.c

## Purpose
`renesas_sdhi_sys_dmac.c` is the SDHI front-end for Renesas controllers using external/system DMA channels. It provides older SoC OF configuration, DMA channel acquisition/configuration, bounce-buffer handling for unaligned single SG entries, DMA issue/completion coordination, and delegation to the shared SDHI core.

## Important APIs, Types, And Functions
The file defines OF data for default, RZ, R-Car Gen1, and R-Car Gen2 controllers, plus Gen2 SCC taps. The TMIO DMA ops are `renesas_sdhi_sys_dmac_start_dma()`, `renesas_sdhi_sys_dmac_enable_dma()`, `renesas_sdhi_sys_dmac_request_dma()`, `renesas_sdhi_sys_dmac_release_dma()`, `renesas_sdhi_sys_dmac_abort_dma()`, and `renesas_sdhi_sys_dmac_dataend_dma()`. Direction-specific setup is in `renesas_sdhi_sys_dmac_start_dma_rx()` and `_tx()`, and DMA completion is handled by `renesas_sdhi_sys_dmac_dma_callback()`.

## Control Flow
Probe calls `renesas_sdhi_probe()` with OF match data and system-DMAC ops. DMA request obtains TX and RX channels together, configures slave addresses/widths, allocates a one-page bounce buffer, initializes a completion, and enables SDHI DMA. Per request, start validates two-byte alignment and minimum length. Unaligned single-page SG entries use the bounce buffer; unsupported or failed DMA releases both channels and permanently falls back to PIO. Issue work enables DATAEND IRQ and submits pending DMA. Completion unmaps DMA, waits for TMIO DATAEND completion, then calls `tmio_mmc_do_data_irq()` under the host lock.

## State And Persistence
Runtime state lives in TMIO host channel pointers, `bounce_buf`, `bounce_sg`, `host->sg_ptr`, `host->dma_on`, and `dma_priv.dma_dataend`. No persistent state exists.

## Dependencies And Integration Points
The front-end depends on DMAengine slave channels, optional legacy SHDMA filters/platform channel private data, OF matches, TMIO DMA ops, the SDHI common core, MMC scatterlists, PM runtime callbacks, and system workqueues.

## Risks And Test Signals
Risks include permanent PIO fallback after any DMA setup failure, bounce-buffer copying for TX but not post-copying RX here, completion ordering between DMA and DATAEND, channel-pair all-or-nothing assumptions, and small-transfer bypass. Test signals include Gen1/Gen2/RZ probe, DMA channel configuration, aligned and unaligned read/write paths, small transfer PIO behavior, DMA failure fallback, DATAEND wait completion, abort termination, bounce buffer lifetime, and runtime PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_sys_dmac.c -->
