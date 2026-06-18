# sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.h

## Purpose
This header defines the Zilog channel memory layout and register bit names used by `sunzilog.c`.

## Important APIs, Types, And Functions
`struct zilog_channel` models the control/data byte layout with padding. `struct zilog_layout` models a chip with channel B followed by channel A. `NUM_ZSREGS` and `R7p` define the cached write-register array shape. `BRG_TO_BPS()` and `BPS_TO_BRG()` convert between baud and baud-rate-generator constants.

The macros name write registers R0-R15, ESCC R7 prime, write commands, receive/transmit enable fields, parity/stop/clock modes, DTR/RTS/break bits, baud generator controls, interrupt enable bits, read status bits, interrupt-pending codes, and utility clear macros.

## Control Flow
There is no executable control flow. The driver uses these definitions to build register images, decode interrupt pending status, check RX/TX readiness, handle break/error conditions, and convert termios into Zilog register values.

## State And Persistence
The header does not store state. It defines the constants used by `curregs[NUM_ZSREGS]`, which is the driver's persistent in-memory representation of each channel's hardware programming.

## Dependencies And Integration Points
The layout and bits are private to the Sun Zilog driver and assume Linux byte IO helpers are available in the including file. Some legacy macros use `sbus_readb`/`sbus_writeb`, while the current driver primarily uses `readb`/`writeb` wrappers.

## Risks
Incorrect channel order or padding would map channel A/B incorrectly. Register constants overlap by context, so writes must target the intended register. The BRG conversion macros assume valid nonzero baud input. Legacy utility macros are less integrated with the current access wrappers and could be risky if reused casually.

## Test Signals
Practical validation comes from Zilog probe, channel A/B MMIO mapping, BRG programming, interrupt decoding, RX/TX data movement, break/error handling, and ESCC FIFO enable detection in `sunzilog.c`.
