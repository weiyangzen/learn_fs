# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.h

## Purpose

This private header defines the internal onecell clock IDs for the A83T CCU driver.

## Important APIs, types, and functions

It includes A83T clock/reset dt bindings and assigns internal IDs for cluster PLLs, audio/video/VE/DDR/GPU/HSIC/video1 PLLs, CPUX outputs, AXI/AHB/APB buses, `CLK_CCI400`, `CLK_DRAM`, `CLK_MBUS`, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no runtime logic. The constants must match `sun8i_a83t_hw_clks`.

## Dependencies and integration points

The header sits between the public DT binding and the source file’s private clock slots, especially for internal PLLs and non-exported bus clocks.

## Risks and test signals

Index drift can silently expose the wrong clock to DT consumers. Check `CLK_NUMBER` and all explicit onecell assignments whenever binding IDs change.
