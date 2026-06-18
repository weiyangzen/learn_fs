# sources/distributed-fs/ceph-client/drivers/input/serio/altera_ps2.c

## Purpose

`altera_ps2.c` implements a serio driver for the Altera University Program PS/2 controller. It exposes the memory-mapped PS/2 port as a `SERIO_8042` port for standard keyboard and mouse consumers.

## Important APIs, Types, and Functions

`struct ps2if` stores the serio port and mapped register base. `altera_ps2_rxint()` drains received bytes on interrupt. `altera_ps2_write()`, `altera_ps2_open()`, and `altera_ps2_close()` are serio callbacks. `altera_ps2_probe()` maps resources, requests IRQ, allocates/registers the serio port, and `altera_ps2_remove()` unregisters it. OF compatibles include `ALTR,ps2-1.0` and `altr,ps2-1.0`.

## Control Flow

Probe allocates private state, maps the first memory resource, gets and requests the IRQ, allocates a serio port, assigns callbacks and device metadata, registers the port, and stores driver data. Opening drains pending FIFO data by reading while status high bits indicate data, then writes to the control register to enable RX IRQs. Interrupt handling loops while data/status indicate pending RX and reports the low byte to serio. Closing disables RX IRQs.

## State and Persistence Behavior

Persistent state is the mapped register base and serio port pointer. Hardware state includes the RX interrupt enable bit in the controller control register. Received bytes are not buffered by the driver beyond the interrupt loop.

## Dependencies and Integration Points

The file depends on platform devices, devm MMIO resource mapping, IRQ handling, OF matching, and the serio core. It integrates with standard `atkbd`/`psmouse` consumers through the `SERIO_8042` port.

## Risks and Edge Cases

The status interpretation assumes upper 16 bits indicate RX data availability. Writes do not check TX readiness or errors. The open FIFO drain discards bytes without reporting flags. Serio allocation is not devm-managed but is released by `serio_unregister_port()`.

## Test Signals

Tests should cover OF and platform probe, IRQ receive, open/close interrupt enablement, write behavior under busy hardware, remove cleanup, and standard keyboard/mouse detection through serio.
