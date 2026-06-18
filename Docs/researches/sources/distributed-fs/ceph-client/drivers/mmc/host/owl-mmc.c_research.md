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
