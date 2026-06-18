# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.c

## Purpose
This tiny file declares early OF clock providers for legacy SoCFPGA and Arria10 clock nodes. It is the Device Tree binding dispatch layer that connects compatible strings such as `altr,socfpga-pll-clock` and `altr,socfpga-a10-gate-clk` to the actual initialization routines declared in `clk.h`.

## Important APIs, Types, And Functions
The file uses `CLK_OF_DECLARE()` for six providers: `socfpga_pll_init`, `socfpga_periph_init`, `socfpga_gate_init`, `socfpga_a10_pll_init`, `socfpga_a10_periph_init`, and `socfpga_a10_gate_init`. There are no local data structures or runtime functions beyond these declarations.

## Control Flow
At early boot, the OF clock framework scans matching clock nodes and calls the registered init function for each compatible. The actual parsing, register mapping, and clock registration live in other SoCFPGA clock files; this file only wires compatible strings to those entry points.

## State And Persistence
No local state is stored. Persistent effects occur in the called init routines, which register clocks and may map global clock-manager bases.

## Dependencies And Integration Points
It depends on `<linux/of.h>` and the SoCFPGA-local declarations in `clk.h`. It integrates with CCF early clock setup rather than a platform driver probe path.

## Risks
Compatible string typos here prevent entire legacy SoCFPGA clock classes from registering. Because this is early boot code, failures may surface as downstream consumer probe deferrals or timer/console breakage rather than direct errors in this file.

## Test Signals
Boot tests on legacy SoCFPGA and Arria10 DTBs should show that all compatible clock nodes call their expected init routines. Static checks can verify the compatible strings match binding documents and DTS usage.
