# sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang.c

## Purpose
Provides reusable SPI controller utilities for simple polling and bitbanging host drivers. It adapts per-word bitbang callbacks or transfer-at-a-time callbacks into Linux SPI controller setup, transfer, chip-select, registration, and teardown behavior.

## Important APIs, Types, And Functions
Internal `struct spi_bitbang_cs` stores per-device half-period delay, selected `txrx_word` callback, and selected buffer-transfer routine. Exported functions are `spi_bitbang_setup_transfer()`, `spi_bitbang_setup()`, `spi_bitbang_cleanup()`, `spi_bitbang_init()`, `spi_bitbang_start()`, and `spi_bitbang_stop()`. Buffer helpers handle 8-, 16-, and 32-bit words. Controller callbacks installed by `spi_bitbang_init()` include prepare/unprepare hardware, transfer_one, and optional set_cs.

## Control Flow
Setup allocates `spi->controller_state` if needed, selects a mode-specific word transfer callback from `bitbang->txrx_word[]`, configures bits-per-word and delay, and optionally sets MOSI idle. During a transfer, `spi_bitbang_transfer_one()` calls any setup-transfer hook, runs `bitbang->txrx_bufs()`, translates partial positive byte counts to `-EREMOTEIO`, finalizes the current transfer, and returns status. The default `spi_bitbang_bufs()` handles 3-wire direction changes and no-RX/no-TX flags before dispatching to the selected per-width loop. `spi_bitbang_start()` initializes callbacks and registers the SPI controller with an extra reference; `spi_bitbang_stop()` unregisters it.

## State And Persistence
Per-controller state is stored in the caller-provided `struct spi_bitbang`, including lock, busy flag, callbacks, flags, and controller pointer. Per-device state is dynamically allocated as `struct spi_bitbang_cs` and freed in cleanup. The `busy` flag is set during prepare hardware and cleared during unprepare hardware under `bitbang->lock`.

## Dependencies And Integration Points
The file depends on Linux SPI core, `linux/spi/spi_bitbang.h`, workqueue/interrupt headers for framework compatibility, delay/time constants, and module exports. Glue drivers provide `chipselect`, mode-specific `txrx_word` callbacks, optional `txrx_bufs`, optional line-direction and MOSI-idle callbacks, and a preallocated SPI controller.

## Risks And Edge Cases
Controller initialization rejects drivers that already set `transfer` or `transfer_one_message`, because this utility owns `transfer_one`. If GPIO descriptors are used without `SPI_CONTROLLER_GPIO_SS`, a custom chipselect callback is not installed, which can surprise older glue drivers. Bits-per-word above 32 are rejected. Delay calculation can fail for extremely low speeds that exceed `MAX_UDELAY_MS`. The transfer function finalizes even when returning an error, so glue callbacks must not also finalize.

## Test Signals
Test glue drivers using custom chipselects and GPIO descriptors, 8/16/32-bit transfers, 3-wire TX and RX phases, MOSI idle setting, partial-transfer error conversion, setup failure cleanup, registration/unregistration reference behavior, and low-speed delay rejection. Logic analyzer traces should show CS delay and expected clock polarity.
