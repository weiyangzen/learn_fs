# sources/distributed-fs/ceph-client/drivers/tty/serial/zs.h

## Purpose

`zs.h` defines the private data structures and complete Zilog Z85C30 SCC register/bit vocabulary used by the DECstation `zs.c` serial driver. It is both a driver-private state contract and the hardware register map for programming channel control, modem status, baud generator constants, interrupts, and error reporting. The file was read as a complete 285-line header.

## Important APIs, Types, and Functions

Under `__KERNEL__`, `struct zs_port` stores the containing SCC pointer, embedded `uart_port`, clock mode, break/TX-stop state, modem state, current break state, and a 16-byte write-register shadow. `struct zs_scc` groups two channels with a spinlock, atomic IRQ guard, and one-time initialization flag. The conversion macros `ZS_BRG_TO_BPS()` and `ZS_BPS_TO_BRG()` convert between Z85C30 baud-rate-generator constants and baud rates. The rest of the header defines write register numbers `R0`-`R15`, command values, interrupt masks, RX/TX format bits, clock-source bits, modem bits, read-register status bits, and receive error flags.

## Control Flow

The header has no executable control flow. Its constants drive every control path in `zs.c`: register shadow initialization, reset/load sequencing, TX/RX enablement, interrupt decoding, termios translation, modem-line handling, break/sysrq detection, baud generation, and console output.

## State and Persistence Behavior

The header defines the shape of persistent in-memory driver state. The `regs[ZS_NUM_REGS]` shadow is especially important because Z85C30 write registers are programmed repeatedly and not all are safely readable. Hardware state persists in SCC registers; software state persists in static `zs_sccs[]` instances in `zs.c`.

## Dependencies and Integration Points

The structures depend on `struct uart_port`, `spinlock_t`, and `atomic_t` when included in the kernel build. Constants are tightly integrated with the Z85C30 hardware manual and the DECstation IOASIC driver implementation. The baud macros are consumed by termios and validation logic in `zs.c`.

## Risks and Edge Cases

Bit definitions are hardware ABI. A wrong mask can misprogram interrupts, clocking, parity, stop bits, or modem signals. Some names encode historical SCC terminology, so confusing read-register and write-register meanings is easy. The baud macros assume valid nonzero baud and frequency inputs and do not protect against divide-by-zero. Structure layout is private to this driver, but changes must preserve all users in `zs.c`, especially the shared lock and register shadow assumptions.

## Test Signals

Build coverage of `zs.c` is the primary signal. Targeted validation should check baud macro calculations, register-shadow initialization against expected Z85C30 values, interrupt-mask constants against observed RR3/RR0 behavior, modem and break bit interpretation, and compile coverage with and without `CONFIG_SERIAL_ZS_CONSOLE`.
