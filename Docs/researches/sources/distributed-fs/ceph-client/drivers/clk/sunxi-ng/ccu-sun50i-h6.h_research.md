# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.h

Purpose: internal clock-ID header for the H6 main CCU provider. It fills gaps around public DT binding IDs for PLL derivatives and non-exported root clocks.

Important APIs, types, and functions: includes H6 clock/reset binding headers and defines IDs for `CLK_OSC12M`, PLL CPUX/DDR/peripheral/GPU/video/VE/DE/HSIC/audio clocks, CPU and bus roots, `CLK_MBUS`, private DRAM IDs, and `CLK_NUMBER`.

Control flow: no code executes; the C driver uses these macros as indexes in onecell clock storage.

State and persistence: no state. The IDs determine provider array layout and must match references in `ccu-sun50i-h6.c`.

Dependencies and integration points: coupled to `dt-bindings/clock/sun50i-h6-ccu.h` and reset bindings. Comments identify clocks exported for PRCM, DVFS, PIO, and module consumers.

Risks and test signals: ID drift causes consumers to acquire the wrong clock or fail probing. Compile-time use catches missing names; runtime test signals are successful DT lookups for CPUX, APB1, MBUS, module clocks, and reset consumers.
