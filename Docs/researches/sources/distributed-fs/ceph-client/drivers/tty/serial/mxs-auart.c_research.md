# sources/distributed-fs/ceph-client/drivers/tty/serial/mxs-auart.c

## Purpose

`mxs-auart.c` is the Freescale MXS/i.MX23/i.MX28 Application UART driver with Alphascale ASM9260 support. It registers up to five `ttyAPP` ports, supports console output, optional DMA for i.MX28 hardware flow-control configurations, modem-control GPIO integration, and vendor-specific register offset tables for STMP37xx-style and ASM9260-style AUART blocks.

The driver translates serial-core callbacks into AUART register operations, manages reset/clock state, handles RX/TX interrupts, optionally drives DMA transfers, and exposes platform devices matched by `"fsl,imx28-auart"`, `"fsl,imx23-auart"`, and `"alphascale,asm9260-auart"`.

## Important APIs, Types, And Functions

`struct mxs_auart_port` wraps `uart_port` with flags, previous modem-control state, device type, vendor register table, clocks, DMA channels/buffers/scatterlists, modem GPIO descriptors, GPIO IRQs, and modem-status IRQ enable state.

Vendor register indirection is defined by `struct vendor_data`, `mxs_asm9260_offsets[]`, `mxs_stmp37xx_offsets[]`, `mxs_reg_to_offset()`, `mxs_read()`, `mxs_write()`, `mxs_set()`, and `mxs_clr()`. This lets common logic address different layouts.

DMA functions include `mxs_auart_dma_init()`, `mxs_auart_dma_exit()`, `mxs_auart_dma_exit_channel()`, `mxs_auart_dma_tx()`, `dma_tx_callback()`, `mxs_auart_dma_prep_rx()`, and `dma_rx_callback()`. PIO RX/TX uses `mxs_auart_rx_char()`, `mxs_auart_rx_chars()`, and `mxs_auart_tx_chars()`.

Modem control is handled by `mxs_auart_set_mctrl()`, `mxs_auart_get_mctrl()`, `mxs_auart_modem_status()`, `mxs_auart_enable_ms()`, `mxs_auart_disable_ms()`, GPIO init/free/request helpers, and `serial_mctrl_gpio.h`.

Serial-core operations are collected in `mxs_auart_ops`, including `set_ldisc` for PPS-on-DCD handling. Probe/remove/init/exit are `mxs_auart_probe()`, `mxs_auart_remove()`, `mxs_auart_init()`, and `mxs_auart_exit()`. Console support is `auart_console_write()`, `auart_console_setup()`, and `auart_console_get_options()`.

## Control Flow

Module init registers the `uart_driver` and platform driver. Probe allocates the port, gets the required `serial` alias as the line number, records RTS/CTS capability from modern or deprecated DT properties, validates the line, determines device type from match data, gets clocks, maps the MMIO resource, fills `uart_port`, selects the vendor register offsets, requests the main IRQ, initializes modem GPIOs and GPIO IRQs, stores the port in `auart_port[]`, deasserts reset, adds the UART port, and logs hardware version or ASM9260 detection.

Startup enables the module clock, either ungates the console port or fully resets/deasserts a non-console port, enables UARTEN, enables RX/timeout/CTS interrupts, resets FIFO size to the PIO default, enables FIFO mode, samples initial modem GPIO status, and marks modem-status IRQs disabled until termios requests them.

The main IRQ handler locks the port, reads status and interrupt state, acknowledges pending AUART interrupt bits, handles GPIO IRQs for modem line changes, handles CTSMIS, drains RX in PIO mode on RX/timeout interrupts, and services TX interrupts through `mxs_auart_tx_chars()`.

TX in DMA mode serializes with `MXS_AUART_DMA_TX_SYNC`, copies bytes out of the xmit FIFO into a DMA buffer, submits a PIO transfer-count command followed by a MEM_TO_DEV transfer, and chains more TX from the callback. In PIO mode it uses `uart_port_tx_flags()` while the TX FIFO is not full and enables/disables TX interrupt based on pending work.

RX in PIO mode reads one character at a time, classifies break/parity/frame/overrun based on `REG_STAT`, applies status masks, handles sysrq, inserts through `uart_insert_char()`, clears status, and pushes the flip buffer. RX DMA prepares a timeout-count PIO command plus DEV_TO_MEM transfer of `UART_XMIT_SIZE`; completion unmaps, reads RX count from status, inserts the received string without per-byte error flags, clears status, pushes the buffer, and immediately starts another RX DMA.

Termios builds line-control bits for word length, parity, stick parity, stop bits, status masks, CREAD, flow control, and baud divisor. DMA is only attempted for i.MX28 with hardware RTS/CTS support and without GPIO RTS/CTS lines. It writes line control and CTRL2, updates timeout, starts RX DMA if enabled, and enables or disables modem-status IRQs based on `UART_ENABLE_MS()`.

Shutdown disables modem-status IRQs, tears down DMA if active, resets or gates the UART depending on console status, and disables the clock.

## State And Persistence Behavior

Runtime state is stored in `auart_port[]` and each `mxs_auart_port`. There is no disk persistence. Flags in `s->flags` encode DMA enabled, TX DMA synchronization, RX DMA readiness, and hardware RTS/CTS capability. `mctrl_prev` persists previous modem-line state so GPIO and CTS interrupts can report deltas.

DMA changes `port.fifosize` to `UART_XMIT_SIZE` while enabled and startup resets it to `MXS_AUART_FIFO_SIZE`. Console writes save/restore CTRL0 and CTRL2 when the transmitter becomes idle, preserving hardware state around synchronous console output.

For ASM9260, both `mod` and `ahb` clocks are prepared during probe and remain enabled until remove; for non-ASM variants, the main clock is acquired but enabled around startup/console operations.

## Dependencies And Integration Points

The driver depends on serial core, tty flip buffers, console, platform/OF, clocks, DMAengine and DMA mapping, GPIO consumer APIs, IRQ APIs, and `serial_mctrl_gpio`. Device tree supplies compatible string, serial alias, optional RTS/CTS property, clock names for ASM9260, MMIO resource, and IRQ.

It integrates with PPS through `set_ldisc`: selecting `N_PPS` sets `UPF_HARDPPS_CD` and enables modem-status monitoring. It integrates with modem-control GPIOs for RTS/CTS/DCD/DSR/RI when pins are not native AUART signals.

## Risks And Edge Cases

DMA support is deliberately constrained because MX23 has DMA erratum 2836 and GPIO-based RTS/CTS is warned as problematic. RX DMA sacrifices precise break/parity/frame reporting by inserting a raw string based on RX count after clearing error bits.

`mxs_auart_dma_tx()` prepares a PIO descriptor and then overwrites `desc` with the data descriptor without explicitly submitting the first descriptor; this relies on DMAengine/controller semantics for `DMA_TRANS_NONE` preparation and is a maintenance-sensitive path.

Probe requires a valid `serial` alias and fails otherwise. Error paths use `auart_port[pdev->id] = NULL` even though the port line comes from the alias; if `pdev->id` differs from `s->port.line`, cleanup can clear the wrong slot.

Main IRQ and GPIO modem IRQs share `mxs_auart_irq_handle()`, so register reads/acks occur even for GPIO IRQ invocation. Native AUART CTS interrupt enable/disable is left as TODO when CTS is not GPIO.

## Test Signals

Test each compatible and register offset table, probe failure without a serial alias, clock enable/disable on ASM9260 and non-ASM variants, console setup/write/restore, PIO RX/TX with break/parity/frame/overrun/sysrq, hardware and GPIO RTS/CTS combinations, modem GPIO IRQ deltas, PPS line discipline, DMA enable only on i.MX28 hardware RTS/CTS, RX DMA timeout/count behavior, TX DMA serialization, shutdown DMA cleanup, and remove cleanup using both `pdev->id` and alias-derived line values.
