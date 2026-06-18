# sources/distributed-fs/ceph-client/drivers/parport/parport_amiga.c

## Purpose
`parport_amiga.c` is the low-level driver for the Amiga built-in parallel port. It adapts Amiga CIA registers to the generic parport operation table despite hardware limitations such as automatic strobe on data access and mostly non-programmable control lines.

## Important APIs, Types, and Functions
The driver defines `pp_amiga_ops`, implementing data, status, IRQ, direction, and state callbacks. `amiga_parallel_probe()` registers one port using `ciaa.prb` and `IRQ_AMIGA_CIAA_FLG`, requests the IRQ with `parport_irq_handler`, announces the port, and stores it in platform device data. `amiga_parallel_remove()` removes the port, frees IRQ, and drops the parport reference.

## Control Flow
Platform probe initializes data lines as outputs and status lines as inputs, calls `parport_register_port()`, requests the CIAA flag interrupt, logs the port, announces it, and returns. Data reads/writes access `ciaa.prb`; status reads translate low CIA bits from `ciab.pra`; direction callbacks switch `ciaa.ddrb`. Control write is intentionally a no-op because the hardware cannot directly drive those PC-style lines.

## State and Persistence
State is held in CIA data/direction registers and saved/restored through `struct parport_state` fields under `u.amiga`. The platform device stores the `struct parport *`. No persistent state exists.

## Dependencies and Integration Points
The driver depends on Amiga platform headers, CIA register globals, platform-driver probing, parport core, and generic IEEE 1284 software operations. It exposes a `platform:amiga-parallel` alias.

## Risks
PC-style control semantics are partly faked, so some IEEE 1284 protocols may be unreliable despite generic ops being present. Reading data also triggers strobe according to the hardware comment. State restore uses direct CIA bit manipulation and must preserve unrelated bits. Interrupt behavior depends on `/ACK` through CIAA flag IRQ.

## Test Signals
Probe should announce an Amiga built-in port with IRQ. Tests should validate data direction changes, status bit translation for BUSY/PAPEROUT/SELECT, interrupt delivery through `parport_irq_handler`, and graceful removal.
