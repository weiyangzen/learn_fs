# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.h

## Purpose

This private header supplies the internal clock-index namespace for `ccu-sun6i-a31.c`. It bridges public dt-binding clock/reset IDs with non-exported internal IDs needed by the onecell array.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun6i-a31-ccu.h` and `dt-bindings/reset/sun6i-a31-ccu.h`, then defines internal IDs such as `CLK_PLL_CPU`, `CLK_PLL_AUDIO_BASE`, `CLK_PLL_AUDIO_*`, `CLK_PLL_VIDEO*`, `CLK_PLL_VE`, `CLK_PLL_DDR`, `CLK_PLL_GPU`, `CLK_PLL9`, `CLK_PLL10`, bus clocks `CLK_AXI`/`CLK_AHB1`/`CLK_APB*`, DRAM clocks `CLK_MDFS`/`CLK_SDRAM*`, MBUS clocks, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no runtime control flow or state. The defines must match the array slots populated by `sun6i_a31_hw_clks`.

## Dependencies and integration points

The header is consumed by the A31 CCU implementation and implicitly by the DT binding contract. Comments identify clock ranges exported by the public binding versus private slots used only inside the driver.

## Risks and test signals

Wrong numeric IDs create miswired OF clock providers even if registration succeeds. `CLK_NUMBER` must remain one past the last exported/internal slot. Test signals are successful boot without missing-provider errors and consumers resolving the expected clock names/IDs.
