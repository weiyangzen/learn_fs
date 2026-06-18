<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/olpc_apsp.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/olpc_apsp.c

## Purpose
`olpc_apsp.c` is the OLPC AP-SP serio driver for XO systems where firmware on a Marvell security processor bit-bangs PS/2 devices. It exposes separate keyboard and touchpad serio ports and demultiplexes bytes from WTM registers.

## Important APIs, types, and functions
- `struct olpc_apsp` stores the device, keyboard and touchpad serio ports, mapped WTM register base, open count, and IRQ.
- `olpc_apsp_write()` waits for command FIFO space and writes a port-tagged byte to `SECURE_PROCESSOR_COMMAND`.
- `olpc_apsp_rx()` acknowledges SP command-complete interrupts, reads `COMMAND_RETURN_STATUS`, selects keyboard or touchpad serio by the upper byte, delivers the lower byte, clears the interrupt, and reports a wakeup event.
- `olpc_apsp_open()` increments a shared open count, verifies the SP command status on first open, and unmasks interrupt 0.
- `olpc_apsp_close()` decrements open count and masks interrupt 0 when the last port closes.
- `olpc_apsp_probe()` maps resources, creates keyboard `SERIO_8042_XL` and touchpad `SERIO_8042` ports, requests the IRQ, enables wakeup, and stores driver data.

## Control flow
The OF platform driver matches `olpc,ap-sp`. Probe maps WTM registers and IRQ, registers the keyboard port first, then the touchpad port, requests the shared IRQ, and enables device wakeup. Runtime writes are tagged with keyboard or touchpad port ID. Runtime interrupts read a tagged return word and forward it to the corresponding serio port. Remove frees the IRQ and unregisters both ports.

## State and persistence
Open count and port pointers are runtime-only. The driver changes the WTM interrupt mask based on whether either serio port is open. It does not persist SP configuration.

## Dependencies and integration points
It depends on OF platform matching, MMIO resource mapping, OLPC/Marvell WTM register semantics, IRQ handling, PM wakeup helpers, and the serio input stack.

## Risks
- `olpc_apsp_open()` increments `open_count` before checking command readiness; if the first open fails, the count is not rolled back in this function.
- FIFO-full handling uses up to 50 ms of `mdelay()`, which blocks in write paths.
- Unknown port tags default to touchpad because the IRQ path uses keyboard only for exact `KEYBOARD_PORT`.
- Keyboard port is registered before touchpad allocation and IRQ request; cleanup handles failures but transient registration ordering matters.

## Test signals
- Device-tree match and resource mapping tests for `olpc,ap-sp`.
- Hardware tests should cover keyboard/touchpad RX demux, command FIFO full timeout, first-open SP-not-ready failure, interrupt masking across two open ports, wakeup events, and remove while ports are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/olpc_apsp.c -->
