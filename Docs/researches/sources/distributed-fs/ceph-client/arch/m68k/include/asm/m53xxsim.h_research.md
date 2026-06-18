<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxsim.h

## Purpose
`m53xxsim.h` is the large ColdFire 532x/53xx SoC register map, covering interrupt routing, clocks, boot setup, FlexBus, GPIO, PLL, system control, SDRAM, EPORT, and I2C.

## Important APIs, Types, and Functions
It defines CPU metadata, interrupt vectors and peripheral IRQs, interrupt controller registers, timer/profile IRQs, UART/FEC/QSPI/timer/reset/power-management bases, a board-specific assembler `m5329EVB_setup` macro and `PLATFORM_SETUP`, chip configuration module bits, FlexBus chip-select registers and masks, exhaustive GPIO data/direction/set/clear/pin-mux/drive-strength bits, generic GPIO aliases, PLL fields, SCM registers, SDRAM controller fields, EPORT registers, and I2C base/size.

## Control Flow, State, and Persistence
Most content is declarative. The assembler setup macro is early-boot control flow: it disables the watchdog, configures core SRAM via `RAMBAR1`, moves the stack into SRAM, and calls `sysinit`.

## Dependencies and Integration Points
It depends on `m53xxacr.h`, `MCF_CLK`, and assembler context for the EVB setup macro. Common ColdFire drivers use the UART, FEC, QSPI, timer, GPIO, SDRAM, FlexBus, and I2C constants.

## Risks
The header contains many absolute addresses; wrong SoC selection causes destructive MMIO writes. The EVB setup macro changes stack location before C code. GPIO and pin-mux bitfields are dense and easy to miscombine.

## Test Signals
Signals include M5329EVB early boot without dBUG initialization, UART console, FEC networking, QSPI, timer/profile IRQs, GPIO and pin-mux behavior, SDRAM sizing, FlexBus external device access, and I2C probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxsim.h -->
