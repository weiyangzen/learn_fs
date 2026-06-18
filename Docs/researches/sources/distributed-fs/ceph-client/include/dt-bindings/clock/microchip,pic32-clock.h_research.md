<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,pic32-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,pic32-clock.h

Purpose: Defines clock output indices for Microchip PIC32 clock bindings.

Important APIs, types, and functions: Exports flat constants for oscillator, FRC, PLL, system, peripheral bus, reference, and USB PLL clocks, ending with `MAXCLKS`. There are no functions, structs, or stateful macros.

Control flow: No logic executes here. The PIC32 clock provider and DT consumers agree on clock index meanings through these defines.

State and persistence: The constants are binding ABI. Actual oscillator selection, divisors, and enable state are maintained by the PIC32 clock hardware and driver.

Dependencies and integration points: Used by PIC32 DTS files, clock-controller bindings, and consumers requiring system, peripheral bus, reference, or USB PLL clocks.

Risks and test signals: Risks are off-by-one `MAXCLKS`, renamed outputs that do not match provider arrays, and confusion between reference clocks and PB clocks. Test with DT compilation, provider registration, serial console, timers, USB, and peripheral bus consumers, plus clk debug output for expected oscillator parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,pic32-clock.h -->
