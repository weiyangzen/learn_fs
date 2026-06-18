# sources/distributed-fs/ceph-client/drivers/input/serio/xilinx_ps2.c

## Purpose
`xilinx_ps2.c` is a platform serio provider for the Xilinx XPS PS/2 controller. It binds through device tree, maps the big-endian MMIO register block, resets the controller, exposes a `SERIO_8042` port, and reports RX/TX error conditions as serio flags.

## Important APIs, types, and functions
`struct xps2data` holds IRQ, spinlock, MMIO base, accumulated serio flags, serio pointer, and device. `xps2_of_probe()` handles DT resource discovery and port registration. `sxps2_open()` requests IRQ and enables RX interrupts. `xps2_interrupt()` acknowledges interrupt status, records parity/timeout flags, receives a byte with `xps2_recv()`, and calls `serio_interrupt()`. `sxps2_write()` writes one byte if TX is not full. `sxps2_close()` disables interrupts and frees IRQ.

## Control flow
Probe resolves the memory resource and IRQ from OF, allocates state, requests the memory region, maps registers, disables interrupts, resets the controller, initializes the serio port, and registers it. The IRQ is requested only when the serio port is opened by a protocol driver. Interrupt status is cleared by writing the read value back to IPISR; RX_FULL triggers a receive and dispatch, while RX_ERR, TX_NOACK, and watchdog timeout set flags that are consumed with the next received byte.

## State and persistence
Hardware state is reset at probe and interrupt-enable state follows open/close. `drvdata->flags` accumulates error state until a byte is reported, then is cleared. There is no saved configuration beyond in-memory platform driver data.

## Dependencies and integration points
The driver uses OF address and IRQ APIs, manual memory-region reservation, big-endian MMIO accessors, platform driver registration, and the serio core. It matches `xlnx,xps-ps2-1.00.a` and feeds normal PS/2 keyboard/mouse drivers.

## Risks
TX writes fail with `-EAGAIN` if the transmitter is full and do not wait or retry. IRQ mapping via `irq_of_parse_and_map()` is not explicitly disposed in remove. Probe and remove use manual MMIO resource handling, so failure paths must preserve ordering. Error flags can be set by interrupts without RX_FULL and then apply to a later byte, which may or may not match hardware intent.

## Test signals
Build with OF/platform support, bind to a Xilinx DT node, validate memory-region conflicts, reset behavior, IRQ open/close lifetime, RX_FULL delivery, RX overflow/error logging, TX full returns, and module unload with the input device open.
