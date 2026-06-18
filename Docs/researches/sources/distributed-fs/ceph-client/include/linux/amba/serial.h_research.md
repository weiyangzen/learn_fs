# sources/distributed-fs/ceph-client/include/linux/amba/serial.h

## Purpose
Provides register offsets and bit definitions for AMBA PL010/PL011 UARTs and several vendor variants, plus small platform-data hooks for AMBA serial drivers.

## Important APIs, Types, And Functions
The file defines PL010/PL011 offsets such as `UART01x_DR`, `UART011_IBRD`, `UART011_LCRH`, `UART011_IMSC`, `UART011_ICR`, and `UART011_DMACR`, ST-specific registers such as `ST_UART011_DMAWM`, and ZTE `ZX_UART011_*` offsets. It exposes bit masks for status, receive errors, modem signals, line control, FIFO trigger levels, interrupt masks/status/clear bits, and DMA enable bits. `struct amba_pl010_data` contains a `set_mctrl()` callback. `struct amba_pl011_data` contains DMA filter parameters, RX polling settings, and optional init/exit callbacks.

## Control Flow, State, And Persistence
There is no stored state in the header. Driver control flow uses the offsets to program UART registers, clear interrupts, configure FIFOs and DMA watermarks, and route DMA channels through the platform hooks. The platform data persists as device configuration for the UART lifetime.

## Dependencies And Integration Points
Uses `linux/bitfield.h`, `linux/bits.h`, and `linux/types.h`. It is consumed by PL010/PL011 serial drivers, early console/uncompress code, DMA-engine integration, and board/vendor-specific register layout handling.

## Risks And Test Signals
The main risk is mixing register layouts: ZTE offsets and ST extensions are not interchangeable with the baseline PL011 map. Incorrect interrupt clear or DMA bits can wedge console I/O. Test signals include boot console output, normal TTY transmit/receive, modem-control changes, DMA RX/TX operation, interrupt storm absence, and build checks for assembly inclusion where only constants are valid.
