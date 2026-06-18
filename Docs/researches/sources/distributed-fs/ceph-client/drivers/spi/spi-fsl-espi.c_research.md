# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-espi.c

## Purpose
Implements the Freescale enhanced SPI controller driver. It aggregates each SPI message into one hardware transaction, drives TX/RX FIFOs with interrupts, supports dual-output reads through RXSKIP mode, manages per-CS mode registers, and uses runtime PM autosuspend.

## Important APIs, Types, And Functions
`struct fsl_espi` stores device/MMIO state, current message transfer list, TX/RX transfer pointers and positions, completion, swab mode, RXSKIP count, lock, and input clock. Per-device CS state is `struct fsl_espi_cs`. Important functions include `fsl_espi_check_message()`, `fsl_espi_check_rxskip_mode()`, FIFO fill/read helpers, `fsl_espi_setup_transfer()`, `fsl_espi_bufs()`, `fsl_espi_trans()`, `fsl_espi_do_one_msg()`, `fsl_espi_setup()`, `fsl_espi_irq()`, runtime PM callbacks, `fsl_espi_init_regs()`, and `fsl_espi_probe()`.

## Control Flow
Probe gets chip-select count from OF, maps registers, requests IRQ, initializes mode/CS registers from child node properties, enables runtime PM, and registers the controller. A message is validated for maximum length and uniform speed/word size. The driver builds a synthetic transfer with total frame length, maximum delay, and RX bus width, configures CS mode, writes `SPCOM` with chip select, transfer length, optional RXSKIP and dual-output bits, enables interrupts, fills TX FIFO under spinlock, and waits up to two seconds. The ISR reads events/mask, drains RX, refills TX, checks final DON and FIFO counts, clears events, and completes.

## State And Persistence
Per-message state is maintained in TX/RX positions and done flags. Per-device `fsl_espi_cs` caches mode register fields. Runtime PM disables/enables `SPMODE_ENABLE`. Hardware CS registers are reinitialized on resume. No persistent storage is used.

## Dependencies And Integration Points
Depends on Freescale system frequency (`fsl_get_sys_freq()`), OF address/IRQ parsing, runtime PM, SPI core, and compatible `fsl,mpc8536-espi`. It uses SPI core auto runtime PM and max-message-size callbacks.

## Risks
All transfers in a message must share bits-per-word and speed; unsupported mixed messages fail. RXSKIP dual-output mode only supports a write followed by a read and requires the command phase to fit the FIFO. Timeout is fixed at two seconds. FIFO final-state checks log errors but completion has already occurred.

## Test Signals
Uniform and mixed message validation, max transaction length, RXSKIP dual-output flash reads, LSB-first 16-bit byte swapping, runtime suspend/resume, per-CS DT timing fields, FIFO threshold IRQ behavior, and transfer timeout are important tests.
