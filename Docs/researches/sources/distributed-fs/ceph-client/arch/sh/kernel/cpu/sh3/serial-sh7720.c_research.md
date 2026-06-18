# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh7720.c

## Purpose
`serial-sh7720.c` implements SH7720/SH7721 SCIF pin setup for serial ports used by the SH7720 setup file.

## Important APIs, Types, And Functions
It defines `sh7720_sci_init_pins()` and exports `struct plat_sci_port_ops sh7720_sci_port_ops`.

## Control Flow
`sh-sci` invokes `sh7720_sci_init_pins()` through platform data while initializing SCIF0 or SCIF1. The callback selects SoC pin functions appropriate to the port and `cflag`.

## State And Persistence
It changes pin-control hardware state but holds no software state. The serial driver owns runtime UART state.

## Dependencies And Integration Points
`setup-sh7720.c` assigns these ops in both SCIF platform-data structures. It depends on serial core data types and SH7720 pin definitions.

## Risks
SH7720 only exposes two SCIF devices here; wrong pin choices can collide with USB, MMC, or board functions. Termios-dependent hardware-control lines are a likely edge case.

## Test Signals
Boot console, `ttySC0`/`ttySC1` loopback, and board peripheral coexistence with configured pins validate the file.
