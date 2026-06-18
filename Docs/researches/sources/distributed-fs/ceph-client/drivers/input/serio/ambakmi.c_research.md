# sources/distributed-fs/ceph-client/drivers/input/serio/ambakmi.c

## Purpose

`ambakmi.c` implements the ARM AMBA PL050 KMI keyboard/mouse interface as a serio controller. It exposes the KMI hardware as a `SERIO_8042` port and handles clocking, IRQ-driven RX, and byte writes.

## Important APIs, Types, and Functions

`struct amba_kmi_port` stores the serio port, clock, MMIO base, IRQ, divisor, and open flag. `amba_kmi_int()` drains RX interrupts. `amba_kmi_write()`, `amba_kmi_open()`, and `amba_kmi_close()` are serio callbacks. `amba_kmi_probe()` claims AMBA resources, maps registers, gets the KMI clock, and registers the serio port. `amba_kmi_resume()` asks serio to reconnect after system resume.

## Control Flow

Probe requests AMBA regions, allocates private state and serio port, maps registers, gets `KMIREFCLK`, stores IRQ, and registers serio. Opening enables the clock, programs the clock divisor from clock rate, enables the controller, requests the shared IRQ, then enables RX interrupts. Interrupt handling reads KMIDATA while RX interrupt is asserted and reports bytes to serio. Writes busy-wait for TX empty before writing data. Close disables the controller, frees IRQ, and disables the clock.

## State and Persistence Behavior

Persistent state includes the mapped base, clock handle, IRQ, and serio port. Hardware state includes clock enablement, divisor, controller enable, and RX interrupt enable while open. Resume does not restore registers directly; it triggers serio reconnect.

## Dependencies and Integration Points

The driver depends on AMBA bus matching, PL050 register definitions, clock framework, IRQ handling, MMIO accessors, and serio core. It integrates with standard PS/2 protocol drivers via `SERIO_8042`.

## Risks and Edge Cases

Clock divisor calculation assumes a usable clock rate at or above 8 MHz. IRQ is requested on every open and freed on close, so open/close races rely on serio serialization. Write timeout returns `SERIO_TIMEOUT`, not a negative errno. Probe cleanup must release both AMBA regions and separately allocated objects.

## Test Signals

Coverage should include probe/remove, clock enable failure, IRQ request failure, receive interrupt draining, TX timeout, close cleanup, system resume reconnect, and keyboard/mouse operation on PL050 hardware.
