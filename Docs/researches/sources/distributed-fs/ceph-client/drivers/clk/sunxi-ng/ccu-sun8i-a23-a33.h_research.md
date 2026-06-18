# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23-a33.h

## Purpose

This shared private header defines the clock index layout used by both the A23 and A33 CCU drivers.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-a23-a33-ccu.h` and `dt-bindings/reset/sun8i-a23-a33-ccu.h`, then defines internal IDs for PLLs, CPUX, AXI/AHB/APB buses, DRAM/MBUS, and the `CLK_NUMBER` expression based on `CLK_ATS`.

## Control flow, state, and persistence

There is no runtime behavior. The A23 and A33 source files use these constants to initialize their `clk_hw_onecell_data` arrays.

## Dependencies and integration points

The file couples two related SoC drivers to the common DT binding. Comments mark public binding ranges where individual bus and module clocks are exported.

## Risks and test signals

Because this header is shared, adding an A33-only or A23-only clock requires care to keep both onecell tables and `CLK_NUMBER` coherent. Test by booting both compatibles and checking that all binding IDs resolve to the expected clock names.
