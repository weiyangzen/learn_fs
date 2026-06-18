# sources/distributed-fs/ceph-client/drivers/tty/serial/imx.c

## Purpose
`imx.c` is the platform serial-core driver for Motorola/Freescale/NXP i.MX UART controllers. It supports i.MX1 and i.MX21-style register layouts, Device Tree probing, normal TTY operation, console and nbcon output, optional cyclic RX/TX DMA, modem GPIOs, RS485 direction control, console polling, and suspend/resume context management.

## Important APIs, types, and functions
`struct imx_port` embeds `struct uart_port` and stores clock handles, feature flags, mctrl GPIOs, DMA channels and buffers, saved registers, RX flood state, console newline state, RX trigger level, and RS485 TX-state timers. `struct imx_uart_data` and `imx_uart_dt_ids` distinguish compatible variants. `imx_uart_pops` provides serial-core callbacks. DMA support is implemented by `imx_uart_dma_init()`, `imx_uart_start_rx_dma()`, DMA callbacks, and enable/disable helpers. Console paths use `imx_uart_console_write_atomic()`, `imx_uart_console_write_thread()`, setup/exit helpers, and `imx_uart_console`. PM uses context save/restore and wakeup helpers.

## Control flow
Probe allocates `imx_port`, reads the DT serial alias and feature properties, maps MMIO, gets IRQs/clocks, initializes modem GPIOs, reads RS485 defaults, disables interrupt sources, handles RS485 loopback setup, configures DTE/DCEDTE direction, initializes hrtimers, requests split or combined IRQs, records the port in `imx_uart_ports`, and registers it. Startup enables clocks, sets FIFO trigger levels, optionally initializes DMA for non-console ports, soft-resets hardware, clears latches, enables UART/RX/TX and modem sources, starts modem polling, and starts either cyclic RX DMA or PIO RX interrupts. Shutdown terminates DMA, stops TX/RX, handles RS485 RTS release, disables interrupts, deletes timers, and disables clocks.

## State and persistence behavior
State is volatile. Hardware configuration is partly mirrored in `saved_reg[10]` across suspend/noirq. RX DMA uses an in-memory cyclic buffer and `circ_buf` head/tail state. RS485 direction is tracked by `tx_state` plus start/stop hrtimers. Modem state is cached in `old_status` and refreshed by a timer because many modem lines lack IRQs.

## Dependencies and integration points
The file depends on platform devices, Device Tree, clk, pinctrl PM, DMAengine, tty/serial core, sysrq, console/nbcon, mctrl GPIO helpers, timers/hrtimers, and MMIO. DT properties include `uart-has-rtscts`, `fsl,dte-mode`, `rts-gpios`, `fsl,inverted-tx`, `fsl,inverted-rx`, and `fsl,dma-info`.

## Risks and test signals
Risk centers on DMA/PIO parity, RX flood soft-reset heuristics, RS485 low-active RTS limitations, not rewriting unchanged baud registers, suspend/resume clock ordering, wakeup behavior, and requiring valid DT serial aliases. Test PIO and DMA RX/TX, DMA fallback, console/nbcon, sysrq/poll, RS485 with delays and GPIO/non-GPIO RTS, modem polling, custom baud, suspend/resume wakeup, RX flood reproduction, and active termios changes.
