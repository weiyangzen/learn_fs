# sources/distributed-fs/ceph-client/drivers/clk/st/Makefile

## Purpose
This Makefile unconditionally builds the ST clock generator support objects for the `drivers/clk/st` directory: mux, PLL, frequency synthesizer, and flexgen support.

## Important APIs, Types, And Functions
The only build rule is `obj-y += clkgen-mux.o clkgen-pll.o clkgen-fsyn.o clk-flexgen.o`. It does not define code APIs itself, but it determines that all four legacy OF-declared ST providers are linked into the kernel whenever this directory is selected by the parent build.

## Control Flow
There is no runtime control flow. At build time, Kbuild adds the listed objects to built-in objects.

## State And Persistence
No persistent state is held here. The operational state lives in the compiled C files and their hardware registers.

## Dependencies And Integration Points
The rule integrates with the parent clock Kbuild. Because the objects are `obj-y`, availability is controlled by directory inclusion rather than per-object Kconfig symbols in this file.

## Risks
Since all objects build together, compile failures in any one ST clockgen file can break the whole directory. There is no fine-grained module gating here.

## Test Signals
Build coverage for ST clock support should compile all four objects and verify that the corresponding `CLK_OF_DECLARE` providers are present in the final image.
