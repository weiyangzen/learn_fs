## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_clk.c

### Purpose
This file computes early PIC32MZDA system and peripheral bus clocks directly from oscillator registers before the full common-clock framework is available.

### Important APIs, Types, And Functions
`pic32_get_sysclk()` reads `OSCCON` and `SPLLCON`, decodes oscillator source, PLL input divider, multiplier, output divider, and FRC divider, then returns the current system clock. `pic32_get_pbclk(int bus)` reads the PB divider for a bus and divides the system clock.

### Control Flow
Both functions temporarily `ioremap()` the oscillator block. System clock selection handles FRC, SPLL, POSC, and default unknown oscillator cases. PB clock computes `PB1DIV + ((bus - 1) * 0x10)` and divides by the encoded divider plus one.

### State, Persistence, And Dependencies
There is no persistent local state; mappings are released before return. Dependencies are PIC32 oscillator base address and register encodings.

### Integration Points
Early console uses PBCLK2 for UART baud setup. Timer init uses PBCLK7 to derive `mips_hpt_frequency`.

### Risks
Unknown oscillator sources return zero, which can propagate to baud or timer calculations. `pic32_get_pbclk()` does not validate bus range. Repeated `ioremap()` calls are acceptable early but inefficient.

### Test Signals
Compare boot-reported CPU clock, UART baud accuracy, and timer tick frequency against hardware oscillator/PLL settings for FRC, POSC, and SPLL modes.
