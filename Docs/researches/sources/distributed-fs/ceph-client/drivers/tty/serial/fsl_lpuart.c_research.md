# sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_lpuart.c

Purpose: Freescale/NXP LPUART driver for multiple SoC variants and up to twelve `ttyLP` ports. It supports 8-bit and 32-bit register layouts, little/big-endian 32-bit access, DMA TX/RX, interrupt fallback, RS485 auto RTS, console/earlycon, console polling, runtime PM, system sleep, and wakeup handling.

Important APIs/types/functions: `struct lpuart_port` extends `uart_port` with SoC type, clocks, FIFO sizes, DMA channels/descriptors/cookies/scatterlists, cyclic RX ring, timer, wait queue, CS7 tracking, and DMA idle-interrupt mode. `struct lpuart_soc_data` selects devtype/iotype/register offset/watermark. Operation tables are `lpuart_pops` and `lpuart32_pops`. Key functions include `lpuart_probe()`, startup/shutdown pairs, termios setters, DMA helpers, interrupt handlers, RS485 config, console/earlycon setup, `lpuart_global_reset()`, and PM callbacks.

Control flow: probe matches SoC data, maps MMIO plus offset, selects ops and IRQ handler, gets clocks and DT alias, enables clocks, chooses console object, enables runtime PM, performs reset, reads RS485 mode, adds the port, and requests IRQ. Startup discovers FIFO sizes, requests DMA, configures watermarks, enables RX/TX, and starts DMA if possible. Interrupt mode drains/fills FIFOs. DMA TX maps xmit FIFO scatterlists and advances state on completion. DMA RX uses a cyclic ring with residue tracking and timer or IDLE interrupt to push data to TTY.

State/persistence: per-port state includes clocks, watermarks, FIFO sizes, DMA resources, ring head/tail, residue, timer, `dma_tx_in_progress`, DMA-use flags, and `is_cs7`. Hardware state lives in CTRL/BAUD/FIFO/WATER/MODIR or 8-bit equivalents. Runtime PM state lives in PM core. No disk persistence.

Dependencies/integration: OF compatibles for VF610, LS1021A/LS1028A, i.MX7ULP/i.MX8ULP/i.MX8QXP/i.MXRT1050; platform resources; clocks; DMAengine; scatterlist/circ buffers; serial core; RS485; console/earlycon/poll console; pinctrl PM; runtime/system PM.

Risks: many hardware variants make iotype, offset, endianness, FIFO encoding, and baud clock source critical. DMA RX lifetime is complex around timers, residue, DMA ownership, termios restart, and suspend. Several hardware waits are polling loops. 32-bit break uses TX inversion to avoid known bugs. Shared `lpuart_reg.cons` is mutated by probed port type.

Test signals: every compatible family, 8-bit/32-bit and big-endian paths, IMX earlycon offset, DMA/non-DMA TX/RX, timer and IDLE RX DMA, SysRq during DMA, RS485 polarity, CRTSCTS, termios modes/baud, console/earlycon/poll console, runtime autosuspend/resume, wakeup suspend, and probe/remove unwinding.
