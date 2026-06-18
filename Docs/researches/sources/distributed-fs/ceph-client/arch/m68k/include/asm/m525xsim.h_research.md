<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m525xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m525xsim.h

## Purpose
`m525xsim.h` defines ColdFire 525x SIM, peripheral, GPIO, and interrupt mappings.

## Important APIs, Types, and Functions
It supplies CPU name and bus clock, includes `m52xxacr.h`, and defines interrupt controller registers, vector base and peripheral IRQs, SDRAM/DRAM controls, DMA, UARTs, FEC, QSPI, GPIO banks, pin-assignment masks, PIT/EPORT/reset/I2C registers, and generic GPIO limits.

## Control Flow, State, and Persistence
The file has no code; it is consumed as compile-time MMIO metadata. Persistent state resides in hardware registers addressed by the macros.

## Dependencies and Integration Points
ColdFire common drivers use the UART, FEC, timer, GPIO, QSPI, reset, and interrupt constants. Conditional blocks adapt the map to selected 525x variants.

## Risks
Peripheral base addresses and chip-select GPIO numbers vary between closely related parts; using the wrong config can route drivers to the wrong hardware. Pin-mux masks need read/modify/write care in callers.

## Test Signals
Expected signals are serial console, Ethernet, QSPI chip selects, PIT tick, GPIO bank access, and IRQ delivery on a 525x board. Build coverage should include all variant conditionals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m525xsim.h -->
