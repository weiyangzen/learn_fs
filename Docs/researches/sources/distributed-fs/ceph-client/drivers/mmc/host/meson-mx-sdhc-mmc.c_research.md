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
