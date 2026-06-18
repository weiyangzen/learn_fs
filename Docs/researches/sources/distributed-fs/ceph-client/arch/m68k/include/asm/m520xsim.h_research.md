<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m520xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m520xsim.h

## Purpose
`m520xsim.h` defines register maps and interrupt constants for ColdFire 5207/5208 SoCs.

## Important APIs, Types, and Functions
It defines one interrupt controller at `MCFICM_INTC0`, mask/force/ICR offsets, vector base 64, IRQ derivations for UART, FEC, QSPI, PIT, and I2C, SDRAM controller addresses, EPORT/GPIO registers, pin-assignment bits, PIT bases, UART bases, FEC base/size, QSPI chip selects, reset and power-management registers, and I2C base.

## Control Flow, State, and Persistence
The file is declarative. Hardware state persists in MMIO registers programmed by platform initialization and device drivers.

## Dependencies and Integration Points
It depends on `m52xxacr.h` and constants such as `MCF_CLK`. Generic ColdFire interrupt, GPIO, serial, FEC Ethernet, QSPI, PIT, reset, PM, and I2C code all depend on these names.

## Risks
The SoC uses absolute `0xFC...` addresses rather than MBAR-relative expressions, so memory-map assumptions must match boot setup. GPIO generic aliases start at the chip-select bank, which callers must interpret with the pin numbering model.

## Test Signals
Signals include boot console on all three UARTs, FEC interrupt delivery, PIT tick, GPIO numbering, QSPI chip-select mapping, and software reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m520xsim.h -->
