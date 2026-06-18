<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/maceps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/maceps2.c

## Purpose
`maceps2.c` is the SGI O2 MACE PS/2 controller driver. It creates two serio ports, one for the MACE keyboard PS/2 register block and one for the mouse block.

## Important APIs, types, and functions
- `struct maceps2_data` stores a pointer to a MACE PS/2 port register block and its IRQ.
- `maceps2_write()` waits up to `MACE_PS2_TIMEOUT` 50 us units for `PS2_STATUS_TX_EMPTY`, then writes the transmit register.
- `maceps2_interrupt()` reads one received byte when `PS2_STATUS_RX_FULL` is set and delivers it through `serio_interrupt()`.
- `maceps2_open()` requests the port IRQ, resets the hardware, and enables RX clock, TX, and RX interrupts.
- `maceps2_close()` resets the port and frees the IRQ.
- `maceps2_allocate_port()` allocates and initializes a `SERIO_8042` port for the selected index.
- `maceps2_init()` registers a platform driver, allocates a synthetic platform device, and binds static MACE register/IRQ data.

## Control flow
Module init registers the platform driver, allocates and adds a `"maceps2"` platform device, and initializes the two static `port_data` entries from the global `mace` register mapping. Probe allocates both serio ports and registers them. Each serio open requests its own IRQ and enables the hardware. Remove unregisters both ports. Module exit unregisters the synthetic device and driver.

## State and persistence
The driver uses static arrays for two port data objects and serio pointers plus one synthetic platform device pointer. Hardware control registers are reset/enabled on open and reset on close. No persistent settings are saved.

## Dependencies and integration points
It depends on SGI IP32 MACE architecture headers, platform device infrastructure, IRQ handling, MMIO-like MACE register access, and the serio core.

## Risks
- `maceps2_write()` returns `-1` instead of a standard errno on timeout.
- Interrupt handling ignores parity/framing status bits and forwards only the byte.
- The driver creates its own platform device rather than relying on firmware enumeration.
- Probe registers both ports even though IRQs are only requested later at open time, so IRQ failures are user-visible at open.

## Test signals
- Build on SGI O2/IP32 configurations.
- Hardware tests should cover keyboard and mouse open/close, IRQ request failure, write timeout, RX delivery, unload/reload, and parity/framing error behavior expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/maceps2.c -->
