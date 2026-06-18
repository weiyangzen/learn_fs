<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5441xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5441xsim.h

## Purpose
`m5441xsim.h` maps ColdFire 5441x SoC resources, including multi-controller interrupts and a broad modern peripheral set.

## Important APIs, Types, and Functions
It defines CPU metadata, `MACHINE`, `FPUTYPE`, `IOMEMBASE`, `IOMEMSIZE`, includes `m54xxacr.h`, and maps three interrupt controllers, UARTs, I2C, DSPI, FEC, GPIO/EPORT, DMA/eDMA interrupts, eSDHC, FlexCAN, timers, reset, and pin/peripheral registers.

## Control Flow, State, and Persistence
There is no executable code. Constants are consumed by setup and drivers to program persistent MMIO device state.

## Dependencies and Integration Points
It integrates with ColdFire v4 cache handling, `io_no.h` internal-I/O detection through `IOMEMBASE`, and common serial, Ethernet, SPI, I2C, GPIO, DMA, SDHCI, CAN, and interrupt-controller code.

## Risks
Multiple interrupt controllers and vector bases increase the chance of IRQ misrouting. `IOMEMBASE/IOMEMSIZE` directly affect endian handling in non-MMU I/O. Peripheral register overlap assumptions must match the 5441x manual.

## Test Signals
Build and boot 5441x configs, verify UART/FEC/I2C/DSPI/eSDHC/FlexCAN IRQs, GPIO/EPORT behavior, DMA error interrupts, and correct endian access for internal registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5441xsim.h -->
