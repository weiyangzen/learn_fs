# sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.h

## Purpose

`timbuart.h` defines the Timberdale FPGA UART register offsets, FIFO size, control bits, interrupt/status bits, grouped RX/TX flag masks, and tty major/minor values consumed by `timbuart.c`. The file was read as a complete 46-line header.

## Important APIs, Types, and Functions

There are no functions or types. The important definitions are `TIMBUART_FIFO_SIZE`, register offsets `TIMBUART_RXFIFO` through `TIMBUART_BAUDRATE`, control bits `TIMBUART_CTRL_RTS`, `TIMBUART_CTRL_CTS`, `TIMBUART_CTRL_FLSHTX`, `TIMBUART_CTRL_FLSHRX`, interrupt/status bits such as `TXBF`, `TXBAE`, `CTS_DELTA`, `RXDP`, `RXBF`, `RXTT`, `RXBNAE`, `TXBE`, aggregate masks `RXFLAGS` and `TXFLAGS`, and `TIMBUART_MAJOR`/`TIMBUART_MINOR`.

## Control Flow

The header has no executable control flow. Its masks drive runtime decisions in the driver: RX events trigger FIFO draining or flushing, TX events trigger xmit FIFO pumping, `CTS_DELTA` triggers modem-status wakeups, and control bits manipulate RTS or FIFO flushes.

## State and Persistence Behavior

No state is owned by the header. The values are compile-time constants that define how the driver interprets persistent MMIO register state in Timberdale hardware.

## Dependencies and Integration Points

The only integration point is the Timberdale UART driver. The major/minor definitions align the device with Linux serial numbering, while the offsets and bit masks are the ABI between `timbuart.c` and the FPGA register block.

## Risks and Edge Cases

Any incorrect bit assignment changes interrupt acknowledgement, FIFO flushing, or modem-control behavior globally for the driver. `RXFLAGS` includes several conditions that the driver mostly acknowledges together, so adding new bits without matching error handling could hide hardware events. The comment says "GPIO driver" even though the header is for UART; this is documentation drift but not a runtime issue.

## Test Signals

Build coverage of `timbuart.c` is the primary signal. Hardware or emulator tests should verify that each offset reaches the expected register, that `RXFLAGS`/`TXFLAGS` acknowledgement clears only intended events, and that RTS/CTS and FIFO flush bits behave as documented by the Timberdale FPGA.
