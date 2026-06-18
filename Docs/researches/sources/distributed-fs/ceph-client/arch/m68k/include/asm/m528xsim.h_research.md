<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m528xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m528xsim.h

## Purpose
`m528xsim.h` maps ColdFire 5280/5282 integration registers, interrupts, and GPIO/pin multiplexing.

## Important APIs, Types, and Functions
It defines CPU metadata, dual interrupt controllers, vector base and peripheral IRQs, SDRAM/DMA/UART/FEC/QSPI bases, QSPI chip-select pins, extensive GPIO data/direction/set/clear registers, pin assignment registers, PIT and EPORT bases, QADC and GPT GPIO helper registers, generic GPIO aliases, reset bits, and I2C base.

## Control Flow, State, and Persistence
The header has no runtime control flow. Drivers persist configuration by programming the mapped hardware registers.

## Dependencies and Integration Points
It depends on `MCF_IPSBAR`, `MCF_CLK`, and `m52xxacr.h`, and feeds common ColdFire serial, FEC, QSPI, GPIO, PIT, EPORT, QADC/GPT, reset, and I2C code.

## Risks
The GPIO map spans many named ports and up to 180 pins; generic GPIO users rely on the alias base matching the pin-numbering convention. Timer and QSPI IRQ numbers must match interrupt-controller setup.

## Test Signals
Signals include serial console, FEC transmit/receive interrupts, QSPI chip select operation, PIT tick, GPIO set/clear across multiple ports, and I2C probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m528xsim.h -->
