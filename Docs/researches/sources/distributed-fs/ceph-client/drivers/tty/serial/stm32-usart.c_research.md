# sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.c

## Purpose
This is the STM32 USART platform serial driver. It adapts three STM32 register layouts, F4, F7, and H7, to the Linux `uart_port`/`uart_driver` framework and supports normal tty operation, console and earlycon output, RS485, modem-control GPIOs, DMA-assisted RX/TX, runtime PM, system sleep, and H7 wake-from-low-power behavior.

## Important APIs, Types, And Functions
The driver is centered on the static `stm32_ports[STM32_MAX_PORTS]` array declared in the companion header and the `stm32_usart_driver` registered from `stm32_usart_init()`. `stm32f4_info`, `stm32f7_info`, and `stm32h7_info` provide register offsets and feature flags consumed through `struct stm32_usart_info`.

The `uart_ops` implementation is `stm32_uart_ops`: `startup`, `shutdown`, `set_termios`, `start_tx`, `stop_tx`, `stop_rx`, throttle/unthrottle, `pm`, console poll hooks, and mctrl hooks. Probe flow is `stm32_usart_serial_probe()` -> `stm32_usart_of_get_port()` -> DMA channel discovery -> `stm32_usart_init_port()` -> optional DMA buffer setup -> `uart_add_one_port()`. Remove reverses runtime PM, uart registration, DMA buffers/channels, wake IRQ, and clock enable state.

RX/TX data movement has separate PIO and DMA helpers. `stm32_usart_receive_chars_pio()` reads `RDR`, handles error bits, sysrq, and tty flip insertion. `stm32_usart_receive_chars_dma()` consumes a cyclic coherent RX buffer using DMA residue and `last_res`. `stm32_usart_receive_chars()` selects DMA or PIO and temporarily disables `DMAR` to handle DMA-mode RX errors in PIO. TX uses `stm32_usart_transmit_chars_pio()` or `stm32_usart_transmit_chars_dma()` and falls back to PIO if DMA preparation/submission fails.

## Control Flow
Interrupt handling begins in `stm32_usart_interrupt()`. It handles RS485 transmit-complete polarity changes, receiver timeout, wake-up flags, RX ready/error paths, PIO TX empty, and forced DMA RX flushes. `startup()` requests the IRQ, configures optional RX/TX swap, flushes RX FIFO when supported, starts RX DMA if available, and enables RX plus configured IRQ bits. `shutdown()` terminates TX/RX DMA, disables DMA request bits, waits for transmission complete, flushes FIFOs, clears enable/interrupt bits, and frees the IRQ.

`set_termios()` is the main hardware programming path. It waits for `TC`, disables CR1, flushes FIFOs, computes word length/parity/stop bits, selects 8x or 16x oversampling, programs prescaler/BRR, configures read/ignore masks, sets DMA and FIFO timeout bits, applies hardware flow control, applies RS485, configures wake-on-start-bit, writes CR3/CR2/CR1, then reenables the USART.

## State And Persistence
Persistent driver state is in `struct stm32_port`: mapped `uart_port`, clock, matched register info, DMA channels/buffers, DMA busy flags, RX residue tracking, IRQ masks, FIFO threshold config, RS485/GPIO modem control, pin swap, wake source, `rdr_mask`, and throttled state. No disk state is persisted. Hardware register state is rederived from DT properties, termios, runtime PM, and uart-core callbacks.

## Dependencies And Integration Points
The file depends on platform/OF probing, clocks, DMAengine, coherent DMA allocation, runtime PM, wake IRQ support, pinctrl sleep/idle states, tty flip buffers, serial core, sysrq, console/earlycon infrastructure, and `serial_mctrl_gpio`. Device-tree integration includes `serial` aliases, `st,stm32-uart`, `st,stm32f7-uart`, `st,stm32h7-uart`, `rx-tx-swap`, `wakeup-source`, `uart-has-rtscts`, deprecated `st,hw-flow-ctrl`, and FIFO threshold properties.

## Risks
DMA error recovery is delicate: RX DMA errors require fast PIO draining because the hardware masks DMA requests while FIFO data stacks up. `last_res`/residue handling must remain correct across cyclic wraparound. RS485 RTS polarity and delayed DE timing depend on baud/divisor math and on whether RTS is hardware or GPIO controlled. Sleep wakeup paths temporarily stop RX DMA and manually flush data, so missed ordering can drop wake characters. `set_termios()` rewrites core registers while waiting for `TC`; any timeout can leave partially reprogrammed hardware.

## Test Signals
Useful tests include boot probe on each compatible, fallback operation with missing DMA channels, RX/TX under PIO and DMA, RX error handling during DMA, FIFO threshold DT variants, RS485 with both RTS polarities and delays, `rx-tx-swap`, console and earlycon output, sysrq/break handling, suspend/resume with wakeup-source, runtime PM clock toggling, and CREAD/IGNBRK/IGNPAR termios behavior.
