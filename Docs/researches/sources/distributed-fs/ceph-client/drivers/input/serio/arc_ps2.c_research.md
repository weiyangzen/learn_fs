# sources/distributed-fs/ceph-client/drivers/input/serio/arc_ps2.c

## Purpose

`arc_ps2.c` implements a two-port Synopsys ARC PS/2 controller as two serio `SERIO_8042` ports. It verifies the controller ID, disables interrupts during setup, reports RX bytes from both ports, and tracks basic error counters.

## Important APIs, Types, and Functions

`struct arc_ps2_port` stores per-port data/status addresses and serio port. `struct arc_ps2_data` stores both ports, base address, and interrupt/error counters. `arc_ps2_check_rx()` drains a port. `arc_ps2_interrupt()` checks both ports. `arc_ps2_write()`, `arc_ps2_open()`, and `arc_ps2_close()` implement serio callbacks. `arc_ps2_create_port()` creates each serio port, and `arc_ps2_probe()` maps/probes the controller.

## Control Flow

Probe gets the named IRQ, allocates state, maps MMIO, verifies the hardware ID, inhibits both ports, requests the IRQ, creates and registers two serio ports, and stores driver data. Opening a port enables RX interrupts in that port's status register. The shared interrupt drains each port while RX valid is set, converts frame/overflow status into serio flags, and reports bytes. Writes poll for TX not full before writing. Remove unregisters both ports and logs counters.

## State and Persistence Behavior

The driver persists per-port MMIO addresses and serio ports plus aggregate counters for total interrupts, frame errors, and buffer overflows. Hardware state is port interrupt enablement and FIFO/status contents.

## Dependencies and Integration Points

The file depends on platform devices, OF matching, MMIO accessors, IRQ handling, and serio core. It integrates with keyboard/mouse consumers through two independent serio ports.

## Risks and Edge Cases

`arc_ps2_check_rx()` maps frame errors to `SERIO_PARITY` and buffer overflow to `SERIO_FRAME`, which may be semantically surprising. The RX drain has a timeout and logs hardware-stuck errors. Writes use a short polling loop with no delay. The driver assumes exactly two ports and a fixed register layout.

## Test Signals

Useful tests include controller ID mismatch, two-port keyboard/mouse attach, shared IRQ delivery, RX frame and overflow counters, write timeout, open/close interrupt masking per port, partial port creation failure cleanup, and OF compatible matching.
