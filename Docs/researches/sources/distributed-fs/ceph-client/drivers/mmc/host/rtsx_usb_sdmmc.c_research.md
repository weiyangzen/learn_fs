# sources/distributed-fs/ceph-client/drivers/mmc/host/rtsx_usb_sdmmc.c

## Purpose

`rtsx_usb_sdmmc.c` is the MMC host driver for Realtek USB card-reader SD/MMC slots. It binds to the platform device created by the `rtsx_usb` core, exposes MMC host operations, translates MMC requests into Realtek USB control/bulk command sequences, manages card power and pull controls, and optionally registers an MMC activity LED.

## Important APIs, Types, And Functions

- `struct rtsx_usb_sdmmc` stores the USB reader core pointer, MMC host, current request, mutexes, clock/timing flags, card/removal state, current power mode, over-current state, and optional LED class data.
- `rtsx_usb_sdmmc_ops` implements `.request`, `.set_ios`, `.get_ro`, `.get_cd`, `.start_signal_voltage_switch`, `.card_busy`, and `.execute_tuning`.
- `sd_send_cmd_get_rsp()` handles command-only transfers through USB control-mode command batches and response parsing.
- `sd_read_data()` and `sd_write_data()` use the ping-pong buffer for short or non-512-byte-aligned transfers.
- `sd_rw_multi()` programs ring-buffer DMA registers, submits the command batch in card-in/card-out mode, then transfers scatterlist data over USB bulk pipes.
- `sd_power_on()`, `sd_power_off()`, package-specific pull-control helpers, `sd_set_timing()`, `sd_change_phase()`, and `sd_tuning_rx()` handle rails, pins, timing, and tuning.

## Control Flow

Probe obtains `struct rtsx_ucr` from the parent USB interface, allocates and initializes an `mmc_host`, enables runtime PM, optionally registers a LED class device, and calls `mmc_add_host()`. Requests execute synchronously in `sdmmc_request()` under `ucr->dev_mutex`.

`sdmmc_request()` rejects host removal, stale card state, and over-current status. It records the current request, chooses between command-only, 512-byte/multi-block bulk transfer, and short ping-pong-buffer transfer, sets `bytes_xfered`, refreshes card detection on error, clears `host->mrq`, and completes the request. Multi-block transfers send the command first, perform bulk data movement, send stop when needed, and flush `MC_FIFO_CTL`.

## State And Persistence Behavior

Persistent runtime state lives in `struct rtsx_usb_sdmmc` only. `card_exist` and `ocp_stat` are refreshed in `get_cd()` and gate future requests. `power_mode` prevents duplicate power transitions and controls runtime PM references. `host_removal` blocks callbacks and request processing after remove. `ddr_mode` suppresses RX tuning.

## Dependencies And Integration Points

The driver depends on `<linux/rtsx_usb.h>` for control endpoint register access, command batching, card status, clock switching, bulk data transfer, power/LED helpers, and exclusivity checks. It integrates with USB core parent-interface data, MMC host ops, runtime PM, scatterlists, optional LED class support, and Realtek package-detection macros.

## Risks And Edge Cases

- Card state is cached in `host->card_exist`; transient USB control failures can surface as media removal.
- Over-current status is latched in `ocp_stat` and cleared only on no-card path.
- Bulk transfers use fixed 10-second transfer timeouts and then only one response byte.
- Runtime PM references are tied to MMC power modes, so unmatched power transitions could leak usage counts.
- DDR mode deliberately skips tuning; bad DDR phase defaults would surface as data errors rather than tuning failures.

## Test Signals

Build with `CONFIG_MMC_REALTEK_USB` and LED variants, probe/remove under USB disconnect, card detect and write-protect status, short reads such as EXT_CSD, aligned multi-block bulk reads/writes, SDR50/SDR104 tuning, DDR50 no-tuning behavior, 1.8 V voltage switching, runtime suspend/resume, LED trigger behavior, and OCP recovery.
