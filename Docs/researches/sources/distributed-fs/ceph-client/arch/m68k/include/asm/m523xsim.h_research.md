<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m523xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m523xsim.h

## Purpose
`m523xsim.h` maps ColdFire 523x system integration registers and peripheral interrupt assignments.

## Important APIs, Types, and Functions
The header defines CPU/bus clock constants, dual interrupt controller bases under `MCF_IPSBAR`, interrupt offsets, vector base 64, UART/FEC/QSPI/PIT/I2C IRQs, SDRAM control registers, reset controller bits, UART/FEC/QSPI bases, QSPI chip-select GPIOs, large GPIO data/direction/set/clear banks, generic GPIO aliases, pin assignment registers, PIT bases, EPORT registers, and I2C base.

## Control Flow, State, and Persistence
No runtime code exists here. Register state is controlled by SoC setup and drivers through these address constants.

## Dependencies and Integration Points
It depends on `MCF_IPSBAR`, `MCF_CLK`, and `m52xxacr.h`. It feeds the common ColdFire interrupt controller, serial, Ethernet, SPI, GPIO, timer, reset, and I2C subsystems.

## Risks
The file provides many adjacent GPIO registers where off-by-one offsets can change unrelated pins. The interrupt controller numbering must match vector-base assumptions in common interrupt code.

## Test Signals
Boot a 523x config and verify UART, FEC, QSPI chip-selects, PIT interrupts, GPIO set/clear operations, and reset controller writes against hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m523xsim.h -->
