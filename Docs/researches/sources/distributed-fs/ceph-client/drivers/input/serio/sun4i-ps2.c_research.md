# sources/distributed-fs/ceph-client/drivers/input/serio/sun4i-ps2.c

## Purpose
`sun4i-ps2.c` is a platform serio provider for the Allwinner A10/Sun4i PS/2 host controller. It maps the controller registers, manages its clock and interrupt, exposes a `SERIO_8042` port, and translates hardware FIFO/line status into serio bytes and flags.

## Important APIs, types, and functions
`struct sun4i_ps2data` carries the serio port, device, MMIO base, clock, IRQ, and spinlock. `sun4i_ps2_probe()` allocates and registers the port. `sun4i_ps2_open()` programs line-control, FIFO reset/interrupt bits, clock dividers, and global enable. `sun4i_ps2_interrupt()` drains the RX FIFO and reports bytes. `sun4i_ps2_write()` polls `PS2_FSTS_TXRDY` before writing one byte. `sun4i_ps2_close()` disables interrupts and synchronizes the IRQ.

## Control flow
Probe maps the first memory resource, gets/enables the clock, initializes `struct serio`, disables controller interrupts, obtains the platform IRQ, requests it, then registers the serio port. Opening the port enables error interrupts, FIFO interrupts, the sample clock divider, master mode, bus enable, reset, and interrupt enable. IRQ handling reads line and FIFO status, clears errors, computes serio flags, drains the RX count encoded in FIFO status bits, and finally acknowledges status registers. Removal unregisters the port, frees IRQ, disables/puts the clock, unmaps MMIO, and frees private data.

## State and persistence
The controller configuration is programmed on each serio open and disabled on close. Runtime state is the MMIO register set plus private pointers. There is no persistent software configuration. Clock state persists while the platform device is bound; FIFO and interrupt state is reset during open.

## Dependencies and integration points
The driver depends on platform resources, OF compatible `allwinner,sun4i-a10-ps2`, `clk_get()/clk_prepare_enable()`, `ioremap()`, `request_irq()`, and the serio core. It feeds standard PS/2 protocol drivers through a `SERIO_8042` port.

## Risks
The transmit path busy-waits for up to 10 seconds with no sleep, which can stall callers if hardware never becomes ready. Error flag mapping sets `SERIO_TIMEOUT` from parity error rather than timeout-specific bits, which may misclassify faults. Clock divider calculations assume sane source clock rates and do not check for zero or underflow. Probe uses manual resource management rather than devm helpers, so cleanup ordering is important.

## Test signals
Build with the Sun4i platform option, boot on matching DT hardware, verify clock rates and divider programming, open/close IRQ enable behavior, RX FIFO draining under normal and error status, TX timeout behavior with no device attached, and removal while the serio port is open.
