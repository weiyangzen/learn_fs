<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/rpckbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/rpckbd.c

## Purpose
`rpckbd.c` is the Acorn RiscPC IOMD keyboard controller driver. It presents the IOMD KART keyboard interface as a single PS/2-style serio port.

## Important APIs, types, and functions
- `struct rpckbd_data` stores separate transmit and receive IRQ numbers.
- `rpckbd_write()` waits until the transmit-ready bit is set in `IOMD_KCTRL`, then writes `IOMD_KARTTX`.
- `rpckbd_rx()` drains all available receive bytes from `IOMD_KARTRX` while the RX-ready bit is set and delivers them through `serio_interrupt()`.
- `rpckbd_tx()` is a placeholder TX IRQ handler that returns handled.
- `rpckbd_open()` resets the keyboard state machine, clears one RX byte, requests RX and TX IRQs, and rolls back RX IRQ if TX IRQ request fails.
- `rpckbd_close()` frees both IRQs.
- Probe gets two platform IRQs, allocates data and serio, fills port fields, stores driver data, and registers the port.

## Control flow
The platform driver named `"kart"` probes resources, creates one serio port, and registers it. Open resets hardware and requests IRQs. RX interrupts drain and forward bytes. Close frees IRQs. Remove unregisters the serio port and frees `rpckbd_data`.

## State and persistence
Per-port state is only the two IRQ numbers. Hardware state is reset at open. No persistent settings are saved.

## Dependencies and integration points
It depends on Acorn ARM machine headers, IOMD register accessors, platform IRQ resources, and the serio core.

## Risks
- `rpckbd_write()` busy-waits indefinitely for TX ready.
- The TX IRQ handler does not manage transmit state; it only acknowledges the IRQ.
- Remove frees `rpckbd_data` after unregister but relies on serio core to free the serio object.
- Open requests IRQs each time; failures leave the port unusable until retried.

## Test signals
- Build on RiscPC/IOMD configurations.
- Hardware tests should cover platform IRQ discovery, open reset sequence, RX drain loop, TX-ready wait, IRQ request rollback, close, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/rpckbd.c -->
