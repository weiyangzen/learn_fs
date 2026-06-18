# sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_pci_sdmmc.c

## Purpose

`rtsx_pci_sdmmc.c` is the MMC host driver for Realtek PCIe card-reader SD/MMC slots. It binds as a platform driver exposed by the `rtsx_pci` core, allocates an `mmc_host`, implements the MMC request and host-ops surface, translates MMC commands into Realtek register command sequences, and drives PIO-style ping-pong-buffer transfers or DMA ring-buffer transfers through the PCI reader core.

## Important APIs, Types, And Functions

- `struct realtek_pci_sdmmc` is the persistent host state: platform/core pointers, current `mmc_host`, current request, work item, request mutex, clock/timing flags, ejection state, previous power state, DMA sg counts, and pre-request cookie state.
- `realtek_pci_sdmmc_ops` exports `.pre_req`, `.post_req`, `.request`, `.set_ios`, `.get_ro`, `.get_cd`, `.start_signal_voltage_switch`, `.card_busy`, `.execute_tuning`, and `.init_sd_express` to the MMC core.
- `sd_send_cmd_get_rsp()` builds Realtek command batches for command-only operations, handles R0/R1/R1b/R2/R3 response formats, validates response bits and CRC7, and reconstructs MMC response words.
- `sd_read_data()`, `sd_write_data()`, `sd_read_long_data()`, and `sd_write_long_data()` implement short ping-pong-buffer and long DMA data paths.
- `sd_pre_dma_transfer()`, `sdmmc_pre_req()`, and `sdmmc_post_req()` implement MMC pre-request DMA mapping cookies.
- `sd_change_phase()`, `sd_tuning_rx_cmd()`, `sd_tuning_phase()`, `sd_search_final_phase()`, and `sdmmc_execute_tuning()` implement RX/TX phase tuning.
- `sdmmc_init_sd_express()` switches supported Realtek PCIe readers into SD Express/PCIe-card mode and then marks the legacy SD host as ejected.

## Control Flow

Probe receives a `pcr_handle`, allocates `mmc_host`, initializes host state, registers card-event callbacks in `pcr->slots[RTSX_SD_CARD]`, enables runtime PM, and calls `mmc_add_host()`. MMC requests enter `sdmmc_request()`, which stores `host->mrq`, optionally maps DMA, and schedules `sd_request()`.

`sd_request()` rejects removed/missing cards, asks the Realtek core for exclusive SD-card access, takes `pcr->pcr_mutex`, starts the reader, switches the card clock, selects SD mode/share mode, and dispatches by request shape. Command-only requests call `sd_send_cmd_get_rsp()`. Read/write block commands and SDIO extended block commands use `sd_rw_multi()` and DMA; other data requests use `sd_normal_rw()`. Completion sets `bytes_xfered`, clears `host->mrq`, and calls `mmc_request_done()`.

## State And Persistence Behavior

Runtime state is in `struct realtek_pci_sdmmc`; there is no on-disk persistence. `prev_power_state` suppresses redundant power-on work, `eject` blocks new work after remove or SD Express handoff, clock/timing fields cache the last IOS selection, and DMA cookies persist across MMC pre/post request boundaries through `host->cookie`, `cookie_sg_count`, and `data->host_cookie`.

## Dependencies And Integration Points

The driver depends on `<linux/rtsx_pci.h>` for command batching, DMA mapping/transfer, power, pull control, clock switching, card exclusivity, and slot card events. It integrates with the MMC core through `mmc_host_ops`, platform-driver matching on `DRV_NAME_RTSX_PCI_SDMMC`, Linux runtime PM, scatterlist DMA, PCI config access for SD Express, and Realtek card-detect/write-protect bits.

## Risks And Edge Cases

- `sdmmc_request()` assumes block-style commands with data have a valid `mrq->data`; malformed SDIO extended requests without data would be unsafe because `sdio_extblock_cmd()` reads `data->blksz`.
- Request completion is split between the scheduled worker and remove path, so hot-unplug during transfer is a primary race area.
- Voltage switching toggles or force-stops SD clock via `SD_BUS_STAT`; failure paths must clear toggling.
- Tuning chooses the center of the widest passing phase window and can fail on sparse or marginal phase maps.
- SD Express mode disables SD interrupts and marks the host ejected, so legacy MMC requests must stop after handoff.

## Test Signals

Useful signals include build coverage for `CONFIG_MMC_REALTEK_PCI`, probe/remove logs, hotplug card detection, write-protect reporting, `mmc_test` read/write and multi-block cases, runtime suspend/resume with card present, SDR50/SDR104/DDR50 tuning, 1.8 V voltage switch, card removal during transfer, and SD Express-capable Realtek parts.
