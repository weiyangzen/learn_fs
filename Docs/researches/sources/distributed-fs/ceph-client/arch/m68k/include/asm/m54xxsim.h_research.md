<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxsim.h

## Purpose
`m54xxsim.h` maps ColdFire 547x/548x System Integration Unit resources.

## Important APIs, Types, and Functions
It defines CPU and machine metadata, `FPUTYPE`, `IOMEMBASE/IOMEMSIZE`, interrupt controller offsets, UART bases, system IRQ assignments, slice timer bases, GPIO data/direction/set/clear registers, EPORT registers, pin assignment registers and masks, and I2C base/size.

## Control Flow, State, and Persistence
The header is declarative. Persistent state lives in SIU MMIO registers programmed by platform code and drivers.

## Dependencies and Integration Points
It includes `m54xxacr.h` and feeds `io_no.h` internal-I/O checks, m54xx serial, timer, GPIO, EPORT, I2C, FEC/PSC-related pinmux users, and interrupt setup.

## Risks
`IOMEMBASE` controls endian behavior for ColdFire I/O accessors. Pin assignment registers multiplex many functions, so callers must coordinate read/modify/write updates. IRQ numbers are vector-base-relative.

## Test Signals
Boot M54xx configs, verify UARTs, slice timer tick/profiler, I2C, GPIO/EPORT interrupts, power/reset behavior, and correct internal peripheral endian access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxsim.h -->
