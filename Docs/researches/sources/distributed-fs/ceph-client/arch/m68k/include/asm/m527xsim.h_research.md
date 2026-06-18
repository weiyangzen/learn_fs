<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m527xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m527xsim.h

## Purpose
`m527xsim.h` supports ColdFire 5271 and 5275 variants with shared and variant-specific SIM definitions.

## Important APIs, Types, and Functions
It defines CPU/bus clock, interrupt controllers, vector base, UART/FEC/QSPI/PIT/I2C IRQs, SDRAM and DMA registers, UART/FEC/QSPI bases, QSPI chip selects, variant-specific GPIO PODR/PDDR/PPDSDR/PCLRR banks, generic GPIO aliases and pin limits, pin-assignment registers, PIT/EPORT/reset/I2C registers, and UART enable masks.

## Control Flow, State, and Persistence
No executable flow is present. Conditional preprocessing selects the correct 5271 or 5275 register map.

## Dependencies and Integration Points
It depends on `MCF_IPSBAR`, `MCF_CLK`, and `m52xxacr.h`. Common ColdFire drivers and board setup code use the map for serial, Ethernet, SPI, GPIO, timer, and interrupts.

## Risks
5271 and 5275 differ substantially in GPIO layout, FEC count, QSPI chip selects, and pin masks. Incorrect Kconfig selection can cause writes to unrelated registers. Generic GPIO bases differ by variant.

## Test Signals
Build both 5271 and 5275 configs. Runtime signals include UART enable masks, one or two FEC devices as configured, QSPI chip-select GPIOs, PIT interrupts, and GPIO numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m527xsim.h -->
