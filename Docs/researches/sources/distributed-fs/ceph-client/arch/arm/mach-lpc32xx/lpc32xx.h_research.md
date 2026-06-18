# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/lpc32xx.h

Purpose: Large LPC32xx SoC register map and bit-definition header for early platform code.

Important APIs/types/functions: Defines physical base addresses for AHB/FAB/APB/IRAM/IROM/EMC, clock/power register addresses and bit masks, interrupt/timer/UART/GPIO/USB register access macros, UART clock-mode helpers, and `IO_ADDRESS`, `io_p2v`, `io_v2p` static mapping macros.

Control flow: No executable flow; consumers expand these macros into raw MMIO accesses and map descriptors.

State and persistence: No mutable software state. The file encodes static virtual mapping and hardware register ABI assumptions.

Dependencies and integration points: Integrated across LPC32xx common, serial, PM, suspend, clocksource, GPIO, UART, USB, and miscellaneous drivers that include the SoC header.

Risks: The static `IO_ADDRESS` transform assumes address bits 20-23 are zero for all HW IO. A wrong bit mask or base impacts many low-level accesses. Heavy macro use bypasses typed regmap or DT resource validation.

Test signals: Build coverage across all LPC32xx users plus boot smoke covering serial, timers, GPIO, Ethernet, USB, PM, and suspend.
