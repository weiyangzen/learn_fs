# Research: subset-b-004274

This grouped report covers the MMC/SD host-controller files assigned to `subset-b-004274`. Each section is source-tree aligned and bounded by reconciliation markers so it can be split into the required per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_pci_sdmmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_pci_sdmmc.c

## Purpose

`rtsx_pci_sdmmc.c` is the MMC host driver for Realtek PCIe card-reader SD/MMC slots. It binds as a platform driver exposed by the `rtsx_pci` core, allocates an `mmc_host`, implements the MMC request and host-ops surface, translates MMC commands into Realtek register command sequences, and drives PIO-style ping-pong-buffer transfers or DMA ring-buffer transfers through the PCI reader core.

## Important APIs, Types, And Functions

- `struct realtek_pci_sdmmc` is the persistent host state: platform/core pointers, current `mmc_host`, current request, work item, request mutex, clock/timing flags, ejection state, previous power state, DMA sg counts, and pre-request cookie state.
- `realtek_pci_sdmmc_ops` exports `.pre_req`, `.post_req`, `.request`, `.set_ios`, `.get_ro`, `.get_cd`, `.start_signal_voltage_switch`, `.card_busy`, `.execute_tuning`, and `.init_sd_express` to the MMC core.
- `sd_send_cmd_get_rsp()` builds Realtek command batches for command-only operations, handles R0/R1/R1b/R2/R3 response formats, validates response start/transmission bits and CRC7, and reconstructs MMC response words.
- `sd_read_data()`, `sd_write_data()`, `sd_read_long_data()`, and `sd_write_long_data()` implement short ping-pong-buffer and long DMA data paths.
- `sd_pre_dma_transfer()`, `sdmmc_pre_req()`, and `sdmmc_post_req()` implement MMC pre-request DMA mapping cookies to avoid remapping already-prepared scatterlists.
- `sd_change_phase()`, `sd_tuning_rx_cmd()`, `sd_tuning_phase()`, `sd_search_final_phase()`, and `sdmmc_execute_tuning()` implement RX/TX phase tuning for SDR104/SDR50/DDR50.
- `sd_power_on()`, `sd_power_off()`, `sd_set_power_mode()`, `sd_set_timing()`, `sdmmc_set_ios()`, and `sdmmc_switch_voltage()` bridge MMC power/timing/voltage transitions into Realtek register and card-power calls.
- `sdmmc_init_sd_express()` switches supported Realtek PCIe readers into SD Express/PCIe-card mode and then marks the legacy SD host as ejected.

## Control Flow

Probe receives a `pcr_handle`, allocates `mmc_host`, initializes host state, registers card-event callbacks in `pcr->slots[RTSX_SD_CARD]`, enables runtime PM, and calls `mmc_add_host()`. MMC requests enter `sdmmc_request()`, which stores `host->mrq`, optionally maps DMA, and schedules `sd_request()` on the system workqueue.

`sd_request()` rejects removed/missing cards, asks the Realtek core for exclusive SD-card access, takes `pcr->pcr_mutex`, starts the reader, switches the card clock, selects SD mode/share mode, and then dispatches by request shape. Command-only requests call `sd_send_cmd_get_rsp()`. Read/write block commands and SDIO extended block commands use `sd_rw_multi()` and DMA; other data requests use `sd_normal_rw()` with a temporary buffer and ping-pong-buffer access. Multi-block requests send the stop command explicitly when present. Completion sets `bytes_xfered`, clears `host->mrq`, and calls `mmc_request_done()`.

IOS changes are synchronous under `pcr->pcr_mutex`: bus width, power, timing registers, spread-spectrum depth, vpclk/double-clock flags, initial low-clock mode, and the Realtek core clock are updated. Tuning is similarly serialized under the PCR mutex and scans phase points to choose the center of the widest passing window.

## State And Persistence Behavior

Runtime state is in `struct realtek_pci_sdmmc`; there is no on-disk persistence. `prev_power_state` suppresses redundant power-on work and treats `MMC_POWER_UP` to `MMC_POWER_ON` as a clock-toggle stop. `eject` permanently blocks new work after remove or SD Express handoff. `host->clock`, `ssc_depth`, `vpclk`, `double_clk`, and `initial_mode` cache the last selected clock mode and are reused before every request. DMA cookies persist across MMC pre/post request boundaries through `host->cookie`, `cookie_sg_count`, and `data->host_cookie`.

## Dependencies And Integration Points

The driver depends on the Realtek PCI reader API in `<linux/rtsx_pci.h>` for command batching, DMA mapping/transfer, power, pull control, clock switching, card exclusivity, and slot card events. It integrates with the MMC core through `mmc_host_ops`, platform-driver matching on `DRV_NAME_RTSX_PCI_SDMMC`, Linux runtime PM, scatterlist DMA, PCI config access for SD Express, and card-detect/write-protect bits exposed by the Realtek core.

## Risks And Edge Cases

- `sdmmc_request()` assumes block-style commands with data have a valid `mrq->data`; malformed SDIO extended requests without data would be unsafe because `sdio_extblock_cmd()` reads `data->blksz`.
- Request completion is split between the scheduled worker and remove path; `host_mutex` protects `host->mrq`, but the worker also touches `mrq` local state while remove can complete an unfinished transfer through the Realtek core, so hot-unplug timing is a primary risk.
- Voltage switching toggles or force-stops SD clock via `SD_BUS_STAT`; failure paths need to clear toggling or the card can be left in a confusing electrical state.
- Tuning chooses the largest passing window from repeated scans; marginal hardware, temperature drift, or sparse phase maps can produce `-EINVAL` and mode fallback.
- SD Express mode disables SD interrupts and marks the host ejected, so tests must ensure the legacy host does not continue servicing MMC requests after handoff.

## Test Signals

Useful signals include kernel build coverage for `CONFIG_MMC_REALTEK_PCI`, probe/remove logs, hotplug card detection, write-protect reporting, `mmc_test` read/write and multi-block cases, runtime suspend/resume with card present, SDR50/SDR104/DDR50 tuning, 1.8 V voltage switch, card removal during transfer, and SD Express-capable Realtek parts exercising `init_sd_express`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_pci_sdmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_usb_sdmmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_usb_sdmmc.c

## Purpose

`rtsx_usb_sdmmc.c` is the MMC host driver for Realtek USB card-reader SD/MMC slots. It binds to the platform device created by the `rtsx_usb` core, exposes MMC host operations, translates MMC requests into Realtek USB control/bulk command sequences, manages card power and pull controls, and optionally registers an MMC activity LED.

## Important APIs, Types, And Functions

- `struct rtsx_usb_sdmmc` stores the USB reader core pointer, MMC host, current request, mutexes, clock/timing flags, card/removal state, current power mode, over-current state, and optional LED class data.
- `rtsx_usb_sdmmc_ops` implements `.request`, `.set_ios`, `.get_ro`, `.get_cd`, `.start_signal_voltage_switch`, `.card_busy`, and `.execute_tuning`.
- `sd_send_cmd_get_rsp()` handles command-only transfers through USB control-mode command batches and response parsing.
- `sd_read_data()` and `sd_write_data()` use the ping-pong buffer for short or non-512-byte-aligned transfers.
- `sd_rw_multi()` programs ring-buffer DMA registers, submits the command batch in card-in/card-out mode, then transfers scatterlist data over USB bulk pipes.
- `sd_power_on()`, `sd_power_off()`, and package-specific pull-control helpers configure card rails, SSC power, output enable, and pin pulls.
- `sd_set_timing()`, `sd_change_phase()`, `sd_tuning_rx()`, and `sdmmc_execute_tuning()` configure speed mode and tune the RX phase, skipping tuning in DDR mode.
- `rtsx_usb_led_control()` and `rtsx_usb_update_led()` integrate with `led_classdev` when LED support is enabled.

## Control Flow

Probe obtains `struct rtsx_ucr` from the parent USB interface, allocates and initializes an `mmc_host`, enables runtime PM, optionally registers a LED class device, and calls `mmc_add_host()`. Unlike the PCI variant, requests execute synchronously in `sdmmc_request()` under `ucr->dev_mutex`.

`sdmmc_request()` first rejects host removal, stale card state, and over-current status. It then records the current request, chooses between command-only, 512-byte/multi-block bulk transfer, and short ping-pong-buffer transfer, sets `bytes_xfered`, refreshes card detection on error, clears `host->mrq`, and completes the request. Multi-block transfers send the command first, perform bulk data movement, send stop when needed, and flush `MC_FIFO_CTL`.

IOS changes take the USB device mutex, update power mode, bus width, timing, clocking flags, and call `rtsx_usb_switch_clock()`. Runtime suspend clears polling needs; runtime resume re-enables polling, refreshes card-detect state, and schedules detection if a card is present.

## State And Persistence Behavior

Persistent runtime state lives in `struct rtsx_usb_sdmmc` only. `card_exist` and `ocp_stat` are refreshed in `get_cd()` and gate future requests. `power_mode` prevents duplicate power transitions and controls runtime PM references. `host_removal` blocks callbacks and request processing after remove. `ddr_mode` suppresses RX tuning. LED brightness is stored in the LED classdev and applied asynchronously while holding the USB device mutex.

## Dependencies And Integration Points

The driver depends on `<linux/rtsx_usb.h>` for control endpoint register access, command batching, card status, clock switching, bulk data transfer, power/LED helpers, and exclusivity checks. It integrates with USB core parent-interface data, MMC host ops, runtime PM, scatterlists, optional LED class support, and Realtek package-detection macros for pull-control programming.

## Risks And Edge Cases

- Card state is cached in `host->card_exist`; failed `get_cd()` transitions intentionally behave as no card, so transient USB control failures can surface as media removal.
- Over-current status is latched in `ocp_stat` and cleared only on no-card path; tests should cover recovery after OCP.
- Request removal handling completes the in-flight `mrq` under `host_mutex` without cancelling an independent worker because requests are synchronous, but any concurrent path holding `ucr->dev_mutex` can affect teardown latency.
- The bulk path uses fixed 10-second transfer timeouts and then only one response byte; stalls or short responses need robust USB error propagation.
- Runtime PM uses `pm_runtime_get_noresume()`/`put_noidle()` around power modes, so unmatched power transitions would leak active usage counts.

## Test Signals

Build with `CONFIG_MMC_REALTEK_USB` and LED variants, probe/remove under USB disconnect, card detect and write-protect status, short reads such as EXT_CSD, aligned multi-block bulk reads/writes, SDR50/SDR104 tuning, DDR50 no-tuning behavior, 1.8 V voltage switching, runtime suspend/resume with polling changes, LED trigger behavior, and OCP fault/recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_usb_sdmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-acpi.c

## Purpose

`sdhci-acpi.c` is the ACPI platform glue for SDHCI controllers. It maps ACPI HID/UID combinations to slot descriptions, applies vendor quirks for Intel, Qualcomm, and AMD controllers, wires card-detect GPIOs and DMI quirks, manages runtime/system PM, and registers an SDHCI host through the generic SDHCI core.

## Important APIs, Types, And Functions

- `struct sdhci_acpi_chip` carries reusable `sdhci_ops`, quirks, caps, and PM caps for a controller family.
- `struct sdhci_acpi_slot` describes per-HID/UID slot policy: chip pointer, quirks/caps, flags, private data size, and optional probe/remove/free/setup hooks.
- `struct sdhci_acpi_host` is the SDHCI private state: host, selected slot, platform device, runtime-PM flag, Intel flag, suspend voltage-reset flag, and variable private storage.
- Intel DSM support is implemented by `__intel_dsm()`, `intel_dsm()`, `intel_dsm_init()`, `intel_start_signal_voltage_switch()`, `intel_probe_slot()`, and `intel_setup_host()`.
- Qualcomm PWRCTL interrupt support is handled by `sdhci_acpi_qcom_handler()`, `qcom_probe_slot()`, and `qcom_free_slot()`.
- AMD HS200/HS400 support uses `struct amd_sdhci_host`, `amd_select_drive_strength()`, `sdhci_acpi_amd_hs400_dll()`, `amd_set_ios()`, `amd_sdhci_execute_tuning()`, and `amd_sdhci_reset()`.
- `sdhci_acpi_probe()`, `sdhci_acpi_remove()`, and PM callbacks are the platform-driver lifecycle.

## Control Flow

Probe finds the ACPI companion, applies the first matching DMI quirk, selects a slot from `sdhci_acpi_uids`, powers up the ACPI device, performs Bay Trail IOSF setup/defer logic, allocates `sdhci_host` plus slot private data, maps IRQ and MMIO, and invokes slot-specific probe hooks. It then merges chip and slot quirks/caps into the host, configures card-detect GPIO and DMI-specific pull-up/write-protect/active-high behavior, runs `sdhci_setup_host()`, calls slot setup hooks, and registers with `__sdhci_add_host()`. Runtime PM is enabled only for slots marked `SDHCI_ACPI_RUNTIME_PM`.

System and runtime suspend mark retuning needed when appropriate, suspend the SDHCI host, and optionally use Intel DSM to reset SD signal voltage to 3.3 V on affected systems. Resume reapplies Bay Trail IOSF settings and resumes the host. Remove disables runtime PM, calls slot cleanup hooks, removes the host, and frees slot resources.

## State And Persistence Behavior

Slot and chip tables are static. Runtime state is in `struct sdhci_acpi_host` and vendor private storage. Intel private state caches the DSM function mask and high-speed capabilities; AMD private state tracks whether tuning succeeded and whether the HS400 DLL is enabled. DMI quirks are evaluated at probe and copied into host caps/flags. No state is persisted beyond device lifetime.

## Dependencies And Integration Points

This file integrates ACPI device matching, DMI quirks, GPIO descriptors via `mmc_gpiod_request_cd()`, generic SDHCI setup/add/remove, runtime PM, x86 IOSF MBI on Bay Trail, Intel ACPI DSM methods, Qualcomm secondary IRQs, and AMD eMMC timing callbacks. It depends on `sdhci.h`, MMC PM and slot GPIO APIs, ACPI helpers, and platform resources.

## Risks And Edge Cases

- ACPI tables with missing or inaccurate HID/UID data fall back to default SDHCI ops and may miss board-specific quirks.
- Intel DSM failures are mostly non-fatal; capabilities default to all enabled until DSM high-speed caps are read, so firmware behavior directly affects advertised modes.
- DMI quirks are board-specific and can regress card-detect/write-protect or suspend voltage behavior if system identifiers are too broad or too narrow.
- Qualcomm IRQ setup uses a second platform IRQ only for `QCOM8051`; failure to request it leaves the host running without the extra PWRCTL acknowledgement path.
- AMD HS400 tuning state is sticky across timing changes and resets; tests must cover HS400 retune and reset transitions.

## Test Signals

Build with ACPI, x86 IOSF, Intel/AMD/QCOM devices, and DMI quirk coverage. Runtime signals include ACPI probe by HID/UID, card-detect GPIO polarity and pull-up behavior, Intel voltage DSM calls during CMD11 and suspend, Bay Trail deferred probe, Qualcomm PWRCTL IRQ handling, AMD HS200/HS400 tuning and DLL toggling, runtime PM autosuspend/resume, and system suspend/resume with retune requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-bcm-kona.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-bcm-kona.c

## Purpose

`sdhci-bcm-kona.c` is the SDHCI platform driver for Broadcom Kona controllers. It wraps the generic SDHCI platform layer with Kona-specific top-level reset/init registers, GPIO-driven card-detect emulation, core clock setup, and quirks required by the Kona SD host integration.

## Important APIs, Types, And Functions

- `struct sdhci_bcm_kona_dev` contains `write_lock`, used to serialize delay-sensitive writes to card-detect emulation registers.
- `sdhci_bcm_kona_sd_reset()` asserts and deasserts `KONA_SDHOST_RESET` with polling and mandatory write spacing.
- `sdhci_bcm_kona_sd_init()` enables core interrupt propagation and AHB clock gating.
- `sdhci_bcm_kona_sd_card_emulate()` updates `KONA_SDHOST_CORESTAT` to synthesize controller card-detect and write-protect state from MMC GPIOs.
- `sdhci_bcm_kona_card_event()` is the SDHCI card-event callback that mirrors GPIO card detect into controller status.
- `sdhci_bcm_kona_init_74_clocks()` supplies a 740 us delay after power-up as the platform 74-clock hook.
- `sdhci_bcm_kona_probe()` performs platform init, DT parsing, clock rate/enable, reset/init, `sdhci_add_host()`, and initial card insertion emulation.

## Control Flow

Probe calls `sdhci_pltfm_init()` with Kona ops and quirks, parses DT/MMC properties, requires `f_max`, obtains the core clock, sets the clock rate to `f_max`, enables it, marks non-removable cards as broken-card-detect, resets and initializes the top-level controller, and registers the SDHCI host. For non-removable cards it immediately emulates insertion; for removable cards it samples the GPIO after host registration and emulates insertion when present. Remove delegates SDHCI platform removal and disables the clock.

## State And Persistence Behavior

Runtime state is minimal: the platform private write mutex and the enabled clock. Card-detect state is represented in hardware `CORESTAT`, not in long-lived driver state. There is no persistent storage.

## Dependencies And Integration Points

The file depends on `sdhci-pltfm.h`, generic SDHCI ops, DT/MMC parsing, the common SDHCI platform PM ops, Linux clock framework, regulator header inclusion, and MMC slot GPIO helpers. Device matching is through `"brcm,kona-sdhci"` and deprecated `"bcm,kona-sdhci"`.

## Risks And Edge Cases

- Back-to-back register writes require deliberate delays; removing or shortening them can break boot-time and low-clock card insert/remove behavior.
- `f_max` is mandatory; missing `max-frequency` in DT causes probe failure.
- Card detect is GPIO-driven but must be mirrored into controller status to generate SDHCI events; GPIO polarity or debounce mistakes show up as missing or repeated card events.
- Non-removable devices force broken-card-detection and synthetic insertion, so tests must cover eMMC-style boards separately from removable slots.

## Test Signals

Signals include DT match/probe, required `max-frequency`, clock rate setting, reset timeout logging, card insertion/removal through GPIO, write-protect propagation, non-removable synthetic insertion, basic `mmc_test`, suspend/resume through `sdhci_pltfm_pmops`, and remove clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-bcm-kona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-brcmstb.c

## Purpose

`sdhci-brcmstb.c` supports SDHCI controllers in Broadcom set-top-box and Raspberry Pi style SoCs. It layers per-compatible match data over generic SDHCI platform support, handles non-standard CFG/BOOT registers, clock gating, HS400 enhanced strobe, CQHCI, base-clock overrides, reset quirks, and suspend/resume save-restore.

## Important APIs, Types, And Functions

- `struct brcmstb_match_priv` carries per-SoC cfg init, HS400ES callback, save/restore callback, ops table, and match flags.
- `struct sdhci_brcmstb_priv` stores mapped CFG/BOOT registers, saved register values, runtime flags, base clock state, and match data.
- `sdhci_brcmstb_save_regs()` and `sdhci_brcmstb_restore_regs()` preserve CFG/BOOT registers across low-power states for v1/v2 cores.
- `brcmstb_reset()`, `brcmstb_reset_74165b0()`, and `brcmstb_sdhci_reset_cmd_data()` implement standard and special reset flows, including CQHCI reset deactivation through `sdhci_and_cqhci_reset()`.
- `sdhci_brcmstb_set_clock()` and `sdhci_brcmstb_set_uhs_signaling()` provide non-standard clock and UHS/HS400 programming.
- `sdhci_brcmstb_cfginit_2712()` configures delay-line clocking and forced card presence.
- `sdhci_brcmstb_add_host()` sets up optional CQHCI before adding the SDHCI host.
- `sdhci_brcmstb_probe()`, `sdhci_brcmstb_suspend()`, and `sdhci_brcmstb_resume()` are the lifecycle and PM paths.

## Control Flow

Probe selects match data from DT, enables the optional main clock, initializes an SDHCI host with match-specific ops, records private data, enables CQE if `supports-cqe` is present, maps CFG registers, parses MMC/SDHCI properties, optionally maps BOOT registers for non-removable devices, enables automatic SD clock gating only for non-removable devices on capable SoCs, wires HS400ES callbacks, and runs match-specific cfg init. It reads capabilities, masks UHS caps so DT controls them, applies match quirks, may replace base-clock capability from `clock-frequency` and an `sdio_freq` clock, then adds the host with or without CQHCI.

Suspend saves non-standard registers, disables the base clock, suspends CQHCI when enabled, and delegates to `sdhci_pltfm_suspend()`. Resume resumes SDHCI, re-enables/restores the base clock, restores saved CFG/BOOT registers, and resumes CQHCI.

## State And Persistence Behavior

Register save state is stored in `struct sdhci_brcmstb_saved_regs` inside driver private memory. `priv->flags` records runtime CQE and clock-gating decisions. `base_freq_hz` and `base_clk` persist the optional base-clock override across resume. No state persists after device removal.

## Dependencies And Integration Points

This driver integrates DT matching, SDHCI platform helpers, Broadcom CFG/BOOT register ranges, Linux clocks, `mmc_of_parse()`, CQHCI (`cqhci_init`, `cqhci_suspend/resume`, `sdhci_cqe_*`), and the helper in `sdhci-cqhci.h` to deactivate CQHCI on full SDHCI reset.

## Risks And Edge Cases

- `supports-cqe` mutates the match ops table IRQ callback in place; because ops tables are static per compatible, mixed devices with and without CQE should be reviewed for shared-table side effects.
- Base clock override disables presets because capability-derived presets become inaccurate; high-speed failures can occur if DT clock-frequency is wrong.
- Automatic clock gating is deliberately limited to non-removable devices because SD voltage switching can break with gated clocks.
- Save/restore coverage differs by CFG core version; missing BOOT/CFG mappings may cause resume-only failures.
- CQE enable drains `SDHCI_DATA_AVAILABLE`; stuck buffer state is a known risk before command queue operation.

## Test Signals

Test by compatible string and feature matrix: removable SD, non-removable eMMC, HS400/HS400ES, `supports-cqe`, base-clock override, system suspend/resume with register restore, shutdown suspend, reset timeout behavior on 74165b0, card-busy callback presence, and `mmc_test` plus CQE-heavy I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cadence.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cadence.c

## Purpose

`sdhci-cadence.c` is the SDHCI platform driver for Cadence SD4HC-compatible SD/SDIO/eMMC controllers, including Socionext UniPhier, Pensando Elba, Mobileye EyeQ, and generic Cadence compatibles. It handles Cadence HRS registers, PHY delay programming from DT, software tuning, eMMC mode selection, HS400 enhanced strobe, optional eMMC reset, and Elba byte-lane write control.

## Important APIs, Types, And Functions

- `struct sdhci_cdns_priv` stores HRS and optional write-control MMIO bases, write lock, enhanced-strobe state, private write callback, optional reset control, and parsed PHY parameters.
- `sdhci_cdns_write_phy_reg()`, `sdhci_cdns_phy_param_count()`, `sdhci_cdns_phy_param_parse()`, and `sdhci_cdns_phy_init()` parse and program Cadence PHY delay properties.
- `sdhci_cdns_set_tune_val()`, `sdhci_cdns_execute_tuning()`, and `sdhci_cdns_tune_blkgap()` implement software tuning over Cadence tune values and HS200 block-gap tuning.
- `sdhci_cdns_set_uhs_signaling()` maps MMC timings to Cadence eMMC modes in HRS06 and falls back to generic SDHCI signaling for SD mode.
- Elba-specific `elba_priv_writel()`, `elba_write_l()`, `elba_write_w()`, and `elba_write_b()` serialize byte-lane enables before writes.
- `sdhci_cdns_hs400_enhanced_strobe()` and `sdhci_cdns_mmc_hw_reset()` expose MMC host callbacks.
- `sdhci_cdns_probe()` and `sdhci_cdns_resume()` handle lifecycle and PM reinitialization.

## Control Flow

Probe enables the controller clock, selects match-specific driver data, counts PHY properties, initializes an SDHCI platform host with enough private storage for parsed parameters, stores HRS base and shifts `host->ioaddr` to the SDHCI SRS base, installs the HS400ES callback, runs optional match init such as Elba write-control setup, enables SDHCI v4 mode, reads capabilities with a forced SDHCI 4.00 version, parses DT/MMC properties, parses and writes PHY delay parameters, optionally gets an eMMC reset control and wires `card_hw_reset`, then calls `sdhci_add_host()`.

Tuning scans up to 40 Cadence tune values, records the longest passing streak from `mmc_send_tuning()`, programs the center point, and for HS200 tries read block-gap coefficients using `mmc_read_tuning()`. Resume re-enables the clock, reprograms PHY parameters, and resumes the SDHCI host.

## State And Persistence Behavior

Parsed PHY parameters persist in flexible-array private storage for the device lifetime and are replayed on resume. `enhanced_strobe` mirrors current MMC IOS state. Elba write serialization state is just a spinlock plus write-control base. No state is persisted beyond driver memory.

## Dependencies And Integration Points

Dependencies include SDHCI platform support, DT properties for PHY delays and compatibles, Linux reset controls, clock framework, bitfield helpers, poll helpers, MMC tuning helpers, and generic SDHCI v4 capability handling. Match data controls quirks and Elba-specific accessors.

## Risks And Edge Cases

- PHY writes poll HRS ACK with very short timeouts; slow or wedged hardware causes probe/resume failure.
- Tuning assumes the usable tune register range is 0-39 despite a wider field; marginal boards outside that range would fail tuning.
- Elba byte-lane control requires strict write ordering under `wrlock`; any direct HRS/SRS write bypass can corrupt partial-register writes.
- HS400 enhanced-strobe state must stay synchronized with HRS06 mode transitions.
- Resume replays PHY setup before `sdhci_resume_host()`; missing DT PHY parameters or failed clock enable can produce resume-only I/O failures.

## Test Signals

Test generic and SoC-specific compatibles, all DT PHY delay properties, SDR104 and HS200 tuning success/failure paths, HS200 block-gap tuning, HS400 and HS400ES transitions, optional eMMC reset pulse timing, Elba byte/word/long register writes, suspend/resume PHY replay, and build coverage with `CONFIG_MMC_SDHCI_CADENCE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cadence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cqhci.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cqhci.h

## Purpose

`sdhci-cqhci.h` is a small shared helper for drivers that combine the SDHCI core with CQHCI command queue support. Its role is to coordinate full SDHCI resets with command-queue deactivation without making the SDHCI and CQHCI modules directly depend on each other in every driver.

## Important APIs, Types, And Functions

- Includes `cqhci.h` and `sdhci.h`, making CQHCI and SDHCI types visible to users.
- `sdhci_and_cqhci_reset(struct sdhci_host *host, u8 mask)` is the only helper. If the MMC host advertises `MMC_CAP2_CQE`, the reset mask includes `SDHCI_RESET_ALL`, and `host->mmc->cqe_private` exists, it calls `cqhci_deactivate(host->mmc)` before delegating to `sdhci_reset(host, mask)`.

## Control Flow

The helper is intended to be used as an SDHCI `.reset` operation or from platform reset callbacks. Partial command/data resets skip CQHCI deactivation; full resets deactivate CQHCI first, then perform the normal SDHCI reset.

## State And Persistence Behavior

The helper owns no state. It observes `mmc->caps2` and `mmc->cqe_private` and changes CQHCI runtime state by calling `cqhci_deactivate()`.

## Dependencies And Integration Points

Users include platform drivers such as Broadcom STB and i.MX eSDHC that support CQHCI. The helper integrates SDHCI reset semantics with CQHCI lifecycle expectations and relies on the MMC host capability bit as the guard.

## Risks And Edge Cases

- Drivers must use this helper on full resets when CQE is enabled; using raw `sdhci_reset()` can leave CQHCI state active across a controller reset.
- The helper only deactivates on `SDHCI_RESET_ALL`; if a controller-specific command/data reset also invalidates CQHCI state, that driver needs additional handling.
- Incorrectly set `MMC_CAP2_CQE` or `cqe_private` can either skip required deactivation or call CQHCI when not fully initialized.

## Test Signals

Relevant tests are CQE-enabled I/O followed by full controller reset, suspend/resume with CQHCI, recovery from command/data errors, and driver-specific reset paths verifying `cqhci_deactivate()` precedes SDHCI reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cqhci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-dove.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-dove.c

## Purpose

`sdhci-dove.c` is the compact SDHCI platform driver for Marvell Dove SoC SDHCI controllers. It supplies a few register-read overrides and quirks around missing registers, voltage capabilities, timeout behavior, and DMA, then delegates most behavior to the generic SDHCI platform core.

## Important APIs, Types, And Functions

- `sdhci_dove_readw()` returns zero for missing `SDHCI_HOST_VERSION` and `SDHCI_SLOT_INT_STATUS` registers and otherwise performs a normal 16-bit read.
- `sdhci_dove_readl()` masks `SDHCI_CAN_VDD_300` from the capabilities register.
- `sdhci_dove_ops` wires read overrides plus generic clock, bus-width, reset, and UHS signaling functions.
- `sdhci_dove_pdata` declares quirks for non-simultaneous VDD/power, no busy IRQ, broken timeout, forced DMA, and no HISPD bit.
- `sdhci_dove_probe()` initializes the platform host, enables the clock, parses DT/MMC properties, and adds the host.

## Control Flow

Probe creates an SDHCI platform host with `sdhci_dove_pdata`, obtains an enabled clock with `devm_clk_get_enabled()`, parses MMC DT properties, and calls `sdhci_add_host()`. Remove and PM are generic `sdhci_pltfm_remove` and `sdhci_pltfm_pmops`.

## State And Persistence Behavior

This driver has no custom private state. State is in the generic SDHCI host and platform clock pointer. No persistence exists.

## Dependencies And Integration Points

It integrates with DT compatible `"marvell,dove-sdhci"`, Linux clocks, `mmc_of_parse()`, `sdhci-pltfm`, and the generic SDHCI core. It relies on SDHCI platform PM and removal helpers.

## Risks And Edge Cases

- Returning zero for absent version/slot interrupt registers is a compatibility shim; generic SDHCI code must not require real values from those registers.
- Capability masking removes 3.0 V support; board voltage declarations and regulators must agree with that limitation.
- Forced DMA and broken timeout/no busy IRQ quirks mean timeout and data error behavior should be tested on real hardware, not only by capability inspection.

## Test Signals

Build and DT match coverage, clock enable, capability dump showing no 3.0 V, basic read/write I/O, timeout behavior, busy-command behavior, suspend/resume through platform PM, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-dove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-imx.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-imx.c

## Purpose

`sdhci-esdhc-imx.c` is the large Freescale/NXP i.MX and S32 eSDHC/uSDHC platform driver. It adapts non-standard eSDHC/uSDHC register layout and behavior to the SDHCI core, covers many SoC generations, implements manual and standard tuning, HS200/HS400/HS400ES, CQHCI, pinctrl speed states, card-detect/write-protect policy, clock and power management, and numerous errata workarounds.

## Important APIs, Types, And Functions

- `struct esdhc_soc_data` maps compatibles to flags and quirks such as USDHC, manual/standard tuning, CAP1 availability, HS200/HS400/HS400ES, CQHCI, PM QoS, lost-state PM, broken Auto CMD23, and errata flags.
- `struct esdhc_platform_data` stores board-level WP/CD type, delay-line/tuning/strobe settings, and saved tuning values.
- `struct pltfm_imx_data` stores SoC data, board data, clocks, pinctrl states, actual clock, card type, multiblock workaround state, DDR state, and PM QoS request.
- Register accessors `esdhc_readl_le()`, `esdhc_writel_le()`, `esdhc_readw_le()`, `esdhc_writew_le()`, `esdhc_readb_le()`, and `esdhc_writeb_le()` translate between SDHCI expectations and eSDHC/uSDHC registers.
- `esdhc_pltfm_set_clock()`, `esdhc_pltfm_get_ro()`, and `esdhc_pltfm_set_bus_width()` implement key SDHCI ops.
- `usdhc_execute_tuning()`, `esdhc_reset_tuning()`, `esdhc_prepare_tuning()`, `esdhc_executing_tuning()`, and `usdhc_auto_tuning_mode_sel_and_en()` implement tuning.
- `esdhc_set_uhs_signaling()`, `esdhc_set_strobe_dll()`, and `esdhc_hs400_enhanced_strobe()` implement high-speed timing modes.
- `esdhc_cqe_enable()` and `esdhc_cqhci_ops` integrate command queueing.
- `sdhci_esdhc_imx_probe()`, `sdhci_esdhc_imx_hwinit()`, `sdhci_esdhc_suspend/resume()`, and runtime PM callbacks control lifecycle.

## Control Flow

Probe initializes an SDHCI platform host with i.MX pdata, reads match data, applies SoC quirks and PM QoS, gets and enables `per`, `ipg`, and `ahb` clocks, records the base clock, obtains pinctrl speed states, configures USDHC-specific caps and tuning hooks, applies SoC flags for ADMA errata, HS modes, broken Auto CMD23, HS400ES, and optional CQHCI. It then parses DT board properties and generic MMC/SDHCI properties, initializes hardware registers through `sdhci_esdhc_imx_hwinit()`, adds the host, configures wake capability, and enables runtime PM autosuspend.

The accessor layer rewrites present-state bits, capabilities, current limits, interrupt status bits, transfer mode, command writes, clock control, host control, reset behavior, and watermark levels. For older eSDHC it shadows transfer mode and combines it with command writes; for USDHC it uses `MIX_CTRL` and maps Auto CMD23 bits.

Manual tuning scans delay-cell windows, programs the center of the largest passing window, and sets auto-tuning margins. Standard tuning configures controller tuning registers and handles reset/restore paths. High-speed signaling toggles DDR/HS400/feedback clock bits, selects pinctrl states, and configures strobe DLL for HS400.

PM paths save tuning for powered SDIO wake devices, enable/disable IRQ wake, select pinctrl sleep/default states, suspend/resume SDHCI and CQHCI, gate clocks at runtime suspend, restore clock rate when lost, reinitialize hardware after low-power state, and replay saved tuning.

## State And Persistence Behavior

All state is runtime memory. `pltfm_imx_data` persists SoC flags, board properties, tuning save values, clock handles/rates, current DDR and multiblock workaround state, and PM QoS request. `boarddata.saved_tuning_delay_cell` and related fields survive suspend within driver memory and are restored for SDIO keep-power cases. `actual_clock` is saved across runtime suspend to restore the clock. Hardware state can be lost in low-power modes and is reinitialized from driver state.

## Dependencies And Integration Points

The driver integrates DT compatible data, `mmc_of_parse()`, `sdhci_get_property()`, GPIO CD/WP helpers, pinctrl speed states, three clocks, runtime/system PM, CPU latency QoS, CQHCI, SDHCI platform helpers, generic MMC tuning helpers, and eMMC reset/HS400 host callbacks. It includes `sdhci-cqhci.h` so full resets deactivate CQHCI safely.

## Risks And Edge Cases

- The shared static `sdhci_esdhc_ops.platform_execute_tuning` is assigned during probe when a manual-tuning SoC is seen; because the ops table is global, mixed SoC instances with different tuning flags deserve scrutiny.
- The accessors contain many register translations and side effects; regressions can appear as generic SDHCI failures even when core code is unchanged.
- Errata flags strongly affect ADMA, Auto CMD23, 1.8 V maximum clocks, and low-power state loss. Incorrect compatible data can silently advertise unsafe modes.
- Tuning and saved tuning are timing-sensitive and differ for SD, eMMC, and SDIO. SDIO async interrupt limitations are handled by reducing auto-tuning bus-width checks to DAT0/CMD.
- Runtime suspend gates all clocks and may remove PM QoS; resume error paths must re-enable clocks in the right order and remove PM QoS on failure.
- CQHCI enable must drain pending buffer data and clear HALT after runtime resume to avoid queue hangs.

## Test Signals

Coverage should include all major compatible families, DT parsing of tuning/pinctrl/strobe properties, SD/eMMC/SDIO card types, GPIO and controller WP/CD, PIO and DMA transfers, Auto CMD23 and RPMB reliable write behavior, manual and standard tuning, SDR50/SDR104/HS200/HS400/HS400ES, CQE I/O and reset, suspend/resume with SDIO wake, runtime PM autosuspend, low-power state loss, and errata-limited 1.8 V clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-mcf.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-mcf.c

## Purpose

`sdhci-esdhc-mcf.c` is the Freescale ColdFire eSDHC platform driver. It adapts a big-endian ColdFire eSDHC controller to the SDHCI core, handles register-offset/endian differences, clock divisor calculation, limited bus-width/card-detect platform data, DMA endian swapping, and ColdFire-specific quirks.

## Important APIs, Types, And Functions

- `struct pltfm_mcf_data` stores three clocks, shadow transfer mode (`aside`), and current bus-width bits.
- `esdhc_mcf_writeb_be()`, `esdhc_mcf_writew_be()`, `esdhc_mcf_writel_be()`, `esdhc_mcf_readb_be()`, `esdhc_mcf_readw_be()`, and `esdhc_mcf_readl_be()` adapt SDHCI byte/word/long accesses to ColdFire register layout.
- `esdhc_mcf_pltfm_set_clock()` calculates divisors from ColdFire PLL registers and applies eSDHC clock-control bits.
- `esdhc_mcf_reset()` restores bus width and interrupt enables after reset.
- `esdhc_mcf_request_done()` swaps 32-bit words after DMA reads; `esdhc_mcf_copy_to_bounce_buffer()` swaps writes copied to the bounce buffer.
- `esdhc_mcf_plat_init()` interprets `mcf_esdhc_platform_data` for card-detect and max bus width.
- `sdhci_esdhc_mcf_probe()` initializes clocks, platform data, bounce-buffer requirement, SDHCI setup, and host registration.

## Control Flow

Probe allocates a platform SDHCI host with ColdFire private data, disables SDMA boundary, enables Auto CMD12, obtains `ipg`, `ahb`, and `per` clocks, enables them in order, initializes card-detect and bus-width policy from platform data, calls `sdhci_setup_host()`, requires the bounce buffer, and registers with `__sdhci_add_host()`. Remove unregisters the host and disables all clocks.

During requests, generic SDHCI code calls the custom accessors. Transfer mode writes are shadowed and combined with command writes; STOP commands are marked as abort. DMA error bit 28 is remapped to SDHCI ADMA error. Read-completion and write-bounce callbacks compensate for missing hardware DMA-endian selection.

## State And Persistence Behavior

Private state persists clock handles, a pending transfer-mode shadow, and current bus width. Bus width is restored after resets. No persistent storage exists.

## Dependencies And Integration Points

The file depends on platform data from `<linux/platform_data/mmc-esdhc-mcf.h>`, ColdFire PLL register macros, `sdhci-pltfm`, shared eSDHC register definitions in `sdhci-esdhc.h`, Linux clocks, MMC core, scatterlist mapping iterators, and SDHCI bounce-buffer support.

## Risks And Edge Cases

- The pdata initializer uses an undesignated value immediately after `.quirks`; in C this initializes the next field (`quirks2`) with `SDHCI_QUIRK2_HOST_NO_CMD23`, but it is easy to misread and fragile for struct layout changes.
- `esdhc_mcf_pltfm_set_clock()` relies on PLL register layout and local variables for best divisor selection; clock corner cases should be tested because requested and actual clocks can diverge.
- DMA read/write endian swapping depends on bounce-buffer and scatterlist lengths; unaligned or unusual transfers are sensitive.
- Platform data is mandatory; probe fails without it, so this is not DT-discoverable like most other drivers in this subset.

## Test Signals

Build ColdFire config coverage, probe with valid/invalid platform data, all three clocks enabled and unwound on failure, 1-bit and 4-bit bus modes, controller/permanent/no card-detect modes, DMA reads and writes with endian validation, CMD12/Auto CMD12 behavior on large cards, timeout handling, reset bus-width restoration, and remove clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-mcf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc.h

## Purpose

`sdhci-esdhc.h` is the shared register and quirk definition header for Freescale/NXP eSDHC-style platform drivers. It centralizes default SDHCI quirks and non-standard eSDHC register offsets/bits used by the i.MX and ColdFire drivers.

## Important APIs, Types, And Functions

- `ESDHC_DEFAULT_QUIRKS` combines common SDHCI quirks: forced 2048 block size, 32-bit DMA address, no busy IRQ, data timeout uses SDCLK, PIO delay, and no HISPD bit.
- Defines eSDHC register offsets for host control, present state, protocol control, system control, system control 2, capabilities 1, tuning block registers, SD clock/timing control, DLL config/status, and DMA system control.
- Defines bit fields for bus width, voltage select, clock enables/dividers, tuning block control, HS400 mode/window, loopback clock, DLL enable/reset/lock, DMA peripheral clock, FIFO flush, and DMA snoop.

## Control Flow

This header has no runtime control flow. Including drivers use these macros in their accessor, clock, reset, tuning, and DMA paths.

## State And Persistence Behavior

No state is defined. The macros describe hardware state manipulated by consumers.

## Dependencies And Integration Points

The header depends on SDHCI quirk constants from `sdhci.h` through its consumers. It is included by `sdhci-esdhc-imx.c` and `sdhci-esdhc-mcf.c` to keep register naming consistent across related eSDHC drivers.

## Risks And Edge Cases

- Shared macros are used by multiple SoC families with different endian and register-layout requirements; changing a bit definition can affect both i.MX and ColdFire behavior.
- `ESDHC_DEFAULT_QUIRKS` encodes policy as well as hardware limitations. New eSDHC variants that do not need one of the quirks must explicitly override behavior in their driver.
- Several registers are non-standard relative to SDHCI; accidental use of generic SDHCI offsets in consumers can bypass these definitions and break hardware-specific paths.

## Test Signals

Validation is indirect through users: i.MX and ColdFire builds, register programming in clock/reset/tuning paths, bus-width transitions, DLL/HS400 support, timeout behavior, and DMA-system-control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-iproc.c

## Purpose

`sdhci-iproc.c` is the SDHCI platform driver for Broadcom iProc, Cygnus, BCM2835/BCM2711, BCM7211A0, and related ACPI-described controllers. It supplies capability overrides, SoC-specific quirks, 32-bit-only register access with shadowing for affected Arasan integrations, clock handling, and generic SDHCI registration.

## Important APIs, Types, And Functions

- `struct sdhci_iproc_data` stores the SDHCI platform data, optional synthetic capabilities, MMC caps, and whether capabilities are missing from hardware.
- `struct sdhci_iproc_host` stores selected data plus shadow command/block registers and shadow-valid flags.
- `sdhci_iproc_readl/readw/readb()` and `sdhci_iproc_writel/writew/writeb()` implement 32-bit-only access and shadowing of block size/count plus transfer mode until command issue.
- `sdhci_iproc_get_max_clock()` uses the platform clock when present or a stored clock rate otherwise.
- `sdhci_iproc_bcm2711_get_min_clock()` raises the minimum clock to 200 kHz to avoid a BCM2711 low-bus-clock hang.
- Static `sdhci_iproc_data` instances encode quirks/caps for Cygnus, generic iProc, BCM2835, BCM2711, BCM7211A0, and ACPI variants.
- `sdhci_iproc_probe()` selects match data, initializes the SDHCI host, parses properties, enables clocks, fakes missing caps when needed, and adds the host.

## Control Flow

Probe obtains match data from OF or ACPI, creates an SDHCI platform host with the corresponding pdata and private state, parses MMC and SDHCI properties, applies extra MMC caps, enables the device clock for OF-described devices, injects synthetic capabilities with `__sdhci_read_caps()` when hardware lacks usable caps, and calls `sdhci_add_host()`. Shutdown delegates to `sdhci_pltfm_suspend()`; remove and PM use generic platform helpers.

For 32-bit-only controllers, 16-bit writes to `BLOCK_SIZE`, `BLOCK_COUNT`, and `TRANSFER_MODE` are cached. When `COMMAND` is written, the driver emits a combined block register write followed by combined transfer/command write, avoiding unsafe back-to-back same-register writes and respecting clock-domain timing delays at low card clocks.

## State And Persistence Behavior

Private state persists selected SoC data and shadowed command/block register values until the next command write. There is no nonvolatile state. Clock pointers and synthetic caps are held in generic host/platform state.

## Dependencies And Integration Points

The driver integrates OF and ACPI matching, SDHCI platform helpers, generic SDHCI PM, Linux clocks, MMC/SDHCI property parsing, and Broadcom/Raspberry Pi/Arasan hardware quirks. It supports ACPI IDs under `CONFIG_ACPI`.

## Risks And Edge Cases

- Shadowed write ordering is critical for affected Arasan cores; bypassing the custom accessors can reintroduce lost register writes.
- Low-clock delays in `sdhci_iproc_writel()` are tied to `host->clock`; incorrect clock state can under-delay writes.
- Synthetic capability data must match hardware. Wrong caps can advertise unsupported voltage, DMA, or speed modes.
- BCM2711 minimum clock is a hang workaround; changing it can affect no-card polling stability.
- ACPI variants may rely on firmware-provided caps rather than DT synthetic caps.

## Test Signals

Test OF and ACPI matching, all SoC data variants, 32-bit accessor shadowing under command issue, no-card polling at low clocks on BCM2711, synthetic caps visibility, SDR/DDR modes allowed by caps, multiblock reads with ACMD12/ACMD23 quirks, suspend/resume, shutdown, and build coverage with and without ACPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-iproc.c -->
