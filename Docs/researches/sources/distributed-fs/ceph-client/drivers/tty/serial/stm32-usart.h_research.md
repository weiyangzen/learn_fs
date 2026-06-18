# sources/distributed-fs/ceph-client/drivers/tty/serial/stm32-usart.h

## Purpose
This header defines the private STM32 USART register model used by `stm32-usart.c`: per-SoC offsets, feature flags, register bit definitions, buffer sizes, and the per-port state container.

## Important APIs, Types, And Functions
`struct stm32_usart_offsets` abstracts F4/F7/H7 register placement. `struct stm32_usart_config` records feature presence such as seven-bit data, RX/TX swap, wakeup, FIFO support, and the USART enable bit position. `struct stm32_usart_info` combines offsets and feature flags for OF match data.

`struct stm32_port` embeds `struct uart_port` and adds clock, match info, DMA channels and coherent buffers, DMA busy flags, interrupt bit caches, cyclic-RX residue state, flow-control flags, FIFO threshold config, wakeup state, RDR masking, GPIO modem-control handle, and DMA residue state. The header also declares the static `stm32_ports` array and `stm32_usart_driver` for shared use inside the translation unit.

## Control Flow
The header has no executable flow, but its constants drive every control path in the C file. Offset fields choose which hardware registers are valid. `UNDEF_REG` gates features not present on older variants. `USART_SR_ERR_MASK`, interrupt masks, FIFO threshold fields, DMA bits, RS485 DE bits, wakeup bits, and flush request bits are used by startup, interrupt, termios, DMA, console, and PM paths.

## State And Persistence
The key persistent runtime state is `struct stm32_port`. It is static per alias id and survives open/close while the driver is loaded. Hardware state is reflected through cached flags and DMA pointers rather than through any filesystem persistence.

## Dependencies And Integration Points
The definitions assume Linux bit helpers such as `BIT`, `GENMASK`, and DMAengine/serial-core types are visible from the including C file. They integrate directly with STM32 OF match data and Linux serial core port registration.

## Risks
Incorrect register offsets or bit definitions can corrupt unrelated USART registers. The `UNDEF_REG` sentinel is central: callers must check it before touching optional registers. Buffer size constants couple the cyclic DMA setup and residue math. Feature booleans must match silicon capabilities or `set_termios()`, wakeup, FIFO, and swap paths will program unsupported bits.

## Test Signals
Header correctness is exercised through compile coverage for all compatibles and runtime probe on F4, F7, H7/MP1-like hardware. Tests should include variants without `icr`, without prescaler, without FIFO, and with H7 wake/FIFO bits.
