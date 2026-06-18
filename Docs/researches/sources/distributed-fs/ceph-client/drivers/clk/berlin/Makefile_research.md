# sources/distributed-fs/ceph-client/drivers/clk/berlin/Makefile

## Purpose
Builds the Marvell Berlin clock support objects. Common AVPLL, PLL, and divider helpers are always built for the directory, while SoC provider files are selected by machine configuration.

## Important APIs, Types, And Functions
The make rules add `berlin2-avpll.o`, `berlin2-pll.o`, and `berlin2-div.o` unconditionally. `bg2.o` is selected for `CONFIG_MACH_BERLIN_BG2` and `CONFIG_MACH_BERLIN_BG2CD`; `bg2q.o` is selected for `CONFIG_MACH_BERLIN_BG2Q`.

## Control Flow
Kbuild compiles the common helper objects and conditionally links the SoC-specific provider object that contains the `CLK_OF_DECLARE` setup function for the configured machine.

## State And Persistence
No runtime state exists in the Makefile. It controls which object files are available in the kernel image.

## Dependencies And Integration Points
Integrates with Kbuild and the Berlin machine configuration symbols. The SoC files depend on the common helper objects being linked.

## Risks And Edge Cases
Because common objects are `obj-y`, they may be built even when no Berlin SoC provider is selected by this local file. Missing config coverage would omit the `CLK_OF_DECLARE` provider and leave DT clock nodes unresolved.

## Test Signals
Build tests for BG2, BG2CD, and BG2Q configurations should show the expected provider object linked with the three common helper objects and no unresolved helper symbols.
