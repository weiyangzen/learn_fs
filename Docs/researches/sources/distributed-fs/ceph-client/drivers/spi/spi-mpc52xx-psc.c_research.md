# sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx-psc.c

## Purpose

`spi-mpc52xx-psc.c` drives the MPC52xx PSC peripheral when configured as SPI. It is distinct from the dedicated MPC52xx SPI controller driver and uses PSC FIFO alarms plus completions to move bytes.

## Important APIs, Types, And Functions

`struct mpc52xx_psc_spi` stores PSC/FIFO MMIO, IRQ, current bits-per-word, and RX completion. `struct mpc52xx_psc_spi_cs` caches speed and word size. Main functions are `mpc52xx_psc_spi_transfer_setup()`, `mpc52xx_psc_spi_activate_cs()`, `mpc52xx_psc_spi_transfer_rxtx()`, `mpc52xx_psc_spi_transfer_one_message()`, `mpc52xx_psc_spi_setup()`, `mpc52xx_psc_spi_port_config()`, and `mpc52xx_psc_spi_isr()`.

## Control Flow, State, And Persistence

Probe reads `cell-index`, maps PSC registers, derives FIFO register address, requests IRQ, configures PSC clocking/SPI mode/FIFO behavior, initializes completion, and registers the controller. Message transfer walks each transfer, updates setup when needed, activates CS on the first or changed transfer, writes a block to the PSC buffer, configures RX alarm/RXRDY interrupt, waits for completion, drains available RX bytes, updates actual length, applies transfer delay, and finalizes the message.

State is volatile PSC register configuration, per-device controller state, and the completion used by the ISR. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on PowerPC MPC52xx PSC helpers, platform/OF properties, MMIO, completions, and SPI core. It matches `fsl,mpc5200-psc-spi` and legacy `mpc5200-psc-spi`.

## Risks And Test Signals

Risks include fixed 20 MHz MCLK assumptions, one-byte RX interrupt special cases, completion with no timeout, limited CS handling compared with newer SPI APIs, and FIFO alarm tuning. Test with varying transfer sizes, exactly one byte, larger-than-FIFO transfers, CPOL/CPHA/LSB modes, interrupt loss, and PSC clock divider validation.
