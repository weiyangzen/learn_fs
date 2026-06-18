# sources/distributed-fs/ceph-client/drivers/spi/spi-mpc512x-psc.c

## Purpose

`spi-mpc512x-psc.c` drives Freescale MPC5121/MPC5125 PSC blocks configured in SPI mode. It adapts two PSC register layouts, controls PSC FIFO slices, and implements message-level transfers with GPIO chip-select support.

## Important APIs, Types, And Functions

`struct mpc512x_psc_spi` stores the PSC type, PSC/FIFO MMIO bases, IRQ, current bits-per-word, master clock rate, and a TX-empty completion. `struct mpc512x_psc_spi_cs` caches per-device bits-per-word and speed. Key functions are `mpc512x_psc_spi_transfer_setup()`, `mpc512x_psc_spi_activate_cs()`, `mpc512x_psc_spi_transfer_rxtx()`, `mpc512x_psc_spi_msg_xfer()`, hardware prep/unprep hooks, `mpc512x_psc_spi_port_config()`, and `mpc512x_psc_spi_isr()`.

## Control Flow, State, And Persistence

Probe selects MPC5121 or MPC5125 layout from OF data, maps PSC/FIFO registers, requests IRQ, enables `mclk` and `ipg`, configures PSC SPI master mode and FIFO slices, and registers the controller. Message transfer iterates transfers, updates speed/word size, asserts CS when needed, sends chunks limited by TX and RX FIFO space, waits for TX FIFO empty interrupt, drains RX with bounded retries, updates actual length, handles delays and CS changes, then finalizes the message.

State consists of PSC/FIFO registers, per-device controller state allocated in setup, and completion-based wait state. No persistent storage exists.

## Dependencies And Integration Points

The file depends on PowerPC MPC52xx PSC definitions, platform/OF, clocks, GPIO descriptors through SPI core, completions, and SPI core. It matches `fsl,mpc5121-psc-spi` and `fsl,mpc5125-psc-spi`.

## Risks And Test Signals

Risks include PSC layout macro mistakes, FIFO size/rxcnt arithmetic, indefinite wait for TX-empty completion, arbitrary RX retry timeout, and EOF/CS-change handling. Test on both PSC variants, low-speed RX completion, TX-only/RX-only/full-duplex, GPIO CS with `cs_change`, clock divider limits, and IRQ loss/error injection.
