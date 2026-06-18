## sources/distributed-fs/ceph-client/drivers/iio/dac/lpc18xx_dac.c

Purpose: Platform IIO voltage-output driver for the NXP LPC18xx DAC. It exposes a single 10-bit DAC channel and explicitly notes that interrupts and DMA are unsupported.

Important APIs/types/functions: `struct lpc18xx_dac` stores `vref`, MMIO base, mutex, and clock. `lpc18xx_dac_read_raw()` reads `LPC18XX_DAC_CR` for raw and reports `vref / 2^10` scale. `lpc18xx_dac_write_raw()` validates 0..1023 and writes `LPC18XX_DAC_CR_BIAS` plus the shifted value, then enables `LPC18XX_DAC_CTRL_DMA_ENA`.

Control flow: Probe maps MMIO, gets clock and `vref`, enables regulator and clock, clears control and conversion registers, and registers one direct-mode IIO channel. Remove unregisters, clears control, disables clock, and disables regulator.

State and persistence: Output value is held in the DAC control register and read back directly; there is no software cache. Power and clock remain enabled while the device is registered.

Dependencies and integration points: Depends on platform resources, a clock, `vref` regulator, MMIO accessors, mutex for write sequences, and OF compatible `nxp,lpc1850-dac`.

Risks and test signals: Verify the raw bit shift/mask, the fixed BIAS behavior, and the unexpected-looking DMA enable bit after direct writes. Tests should cover probe cleanup after regulator or clock failures, raw bounds, scale with changing regulator voltage, and register clear on remove.
