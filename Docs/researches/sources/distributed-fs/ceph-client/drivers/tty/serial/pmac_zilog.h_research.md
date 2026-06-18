# sources/distributed-fs/ceph-client/drivers/tty/serial/pmac_zilog.h

Purpose: private header for the PowerMac Zilog ESCC driver. It defines the runtime port structure, register accessors, baud conversion macros, Z85c30/ESCC register numbers and bit masks, and flag helpers used by `pmac_zilog.c`.

Important APIs/types/functions: `struct uart_pmac_port` embeds `uart_port`, channel mate pointer, MacIO or platform device identity, OF node, port type, `curregs[NUM_ZSREGS]` register shadow array, driver flags, parity mask, previous status byte, MMIO control/data register pointers, and IRQ name. `pmz_get_port_A()` returns the A channel for paired interrupt status reads. `read_zsreg()`, `write_zsreg()`, `read_zsdata()`, `write_zsdata()`, and `zssync()` provide low-level MMIO access. `BRG_TO_BPS()` and `BPS_TO_BRG()` convert between baud and Zilog baud-rate-generator constants. Macros define registers R0-R15/R7P, command bits, RX/TX enables, parity/stop/data-width settings, clocking, modem/status interrupts, read-status bits, and helper macros such as `ZS_CLEARERR()` and `ZS_CLEARFIFO()`.

Control flow: this header has no standalone runtime flow, but it shapes all driver paths. Startup and termios code build `curregs[]` with the masks here, then `pmz_load_zsregs()` writes the values through the accessors. Interrupt code reads R3/R0/R1 bits defined here to decide channel, RX, TX, external status, and line-error handling. Console and polling paths use data/control accessors directly.

State and persistence: `curregs[]` is the software source of truth for most Zilog write registers because many hardware registers are write-only or mode-dependent. Flag macros define persistent driver state for console/open/IrDA/modem/TX/register-update behavior. The accessors directly manipulate MMIO registers; persistence is in the SCC hardware until reset or power loss.

Dependencies and integration points: depends on Linux `struct uart_port`, PowerMac MacIO/device-tree types when `CONFIG_PPC_PMAC` is enabled, platform device type otherwise, and the Zilog ESCC hardware register model. It is included only by the PowerMac Zilog driver in this subset.

Risks: register constants must remain exactly aligned with Z85c30 semantics; incorrect bits can corrupt channel programming globally. `read_zsreg()` writes the register selector before reading nonzero registers, so callers must respect SCC access ordering. `ZS_CLEARFIFO()` blindly reads data three times as a drain primitive. The `to_pmz(p)` cast assumes `struct uart_pmac_port` embeds `uart_port` as its first field; changing structure layout would break it.

Test signals: compile coverage for PPC_PMAC and non-PMAC branches, register shadow initialization against expected bit values for common 9600/38400/115200 termios, channel A/B pairing through `pmz_get_port_A()`, direct accessor behavior in console/polling paths, and static review of any changes to flag or register bit definitions against the ESCC data sheet.
