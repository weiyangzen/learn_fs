# sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.h

## Purpose
`ip22zilog.h` defines the MMIO layout, baud-rate-generator formulas, register numbers, command bits, status bits, interrupt bits, and clearing macros used by the SGI IP22 Zilog SCC serial driver.

## Important APIs, types, and functions
`struct zilog_channel` describes one SCC channel's control and data registers with different byte placement for big-endian and little-endian builds. `struct zilog_layout` lays out channel B followed by channel A. `NUM_ZSREGS`, `BRG_TO_BPS()`, and `BPS_TO_BRG()` size the software register cache and convert between baud and SCC divisors. `R0` through `R15` index the SCC register set. Bit definitions cover interrupt enable, RX/TX enable, parity/stop/clock mode, modem outputs, master interrupt/reset, baud generator, external/status interrupts, RX availability, TX empty, DCD/CTS/SYNC, break/abort, and error status.

## Control flow
The header has no runtime flow except simple macros. `ip22zilog.c` uses the definitions to program `curregs`, convert termios speeds, decode interrupt pending bits, classify receive and modem status, and issue clear commands.

## State and persistence behavior
No state is stored here. The constants define the structure of driver state elsewhere: the 16-byte write-register shadow array, the MMIO channel layout, and SCC hardware bit meanings.

## Dependencies and integration points
The header depends on `asm/byteorder.h` for MMIO layout. It is tightly coupled to `ip22zilog.c` and to Zilog SCC programming. Clearing macros require `writeb()`, `readb()`, and `udelay()` from including code.

## Risks and test signals
Risks include endian-sensitive register offsets, integer baud rounding, clear macros with no built-in locking, and SCC-generic constants being reused without IP22 timing review. Validate struct offsets on target endian builds, baud macro outputs, A/B interrupt decoding, and error/status/FIFO clear behavior through the driver.
