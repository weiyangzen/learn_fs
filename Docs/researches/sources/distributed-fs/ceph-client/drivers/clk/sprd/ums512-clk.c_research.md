# sources/distributed-fs/ceph-client/drivers/clk/sprd/ums512-clk.c

## Purpose
This file is the Unisoc UMS512 clock provider. It describes the SoC clock tree for many independent register regions: PMU PLL gates, analog PHY PLL blocks, AP AHB/AP APB gates, AP composite clocks, AON APB clocks and gates, AUDCP gates, GPU clocks, multimedia clocks, and multimedia gates. It is mostly declarative: the implementation binds Unisoc clock helper macros to register offsets, bitfields, parent data, fixed factors, and dt-binding clock IDs.

## Important APIs, Types, And Functions
The primary exported behavior is through the platform driver `ums512_clk_driver`. `ums512_clk_probe()` uses `device_get_match_data()`, `sprd_clk_regmap_init()`, and `sprd_clk_probe()` to register the `clk_hw_onecell_data` for the matched register block. Each `sprd_clk_desc` contains the common clocks that need regmap-backed registration plus the hardware onecell table exposed to consumers. The file uses Unisoc helpers from `common.h`, `composite.h`, `div.h`, `gate.h`, `mux.h`, and `pll.h`: `SPRD_PLL_*`, `SPRD_SC_GATE_CLK_*`, `SPRD_MUX_CLK_DATA`, `SPRD_COMP_CLK_DATA`, `SPRD_DIV_CLK_HW`, and Linux `CLK_FIXED_FACTOR_*`.

## Control Flow
Device tree compatible strings select one descriptor from `sprd_ums512_clk_ids`. Probe initializes the regmap for that register resource, then publishes the corresponding onecell clock provider. There is no custom rate algorithm in this file; runtime operations are supplied by the shared Unisoc PLL/gate/mux/div/composite implementations selected by the macros.

## State And Persistence
Persistent state is hardware register state in the matched clock block. The static descriptor tables are immutable driver metadata. Some clocks use `CLK_IGNORE_UNUSED` because firmware, hardware DVFS, or co-processors may control them outside the Linux clock API. AUDCP gates also use `SPRD_GATE_NON_AON` because their register behavior differs from always-on gate blocks.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/sprd,ums512-clk.h` for numeric IDs and on matching DTS nodes such as `sprd,ums512-pmu-gate`, `sprd,ums512-ap-clk`, and `sprd,ums512-mm-gate-clk`. Parent clocks are mixed: some are firmware-named external clocks like `ext-26m`, `ext-32k`, `rco-100m`, and others are `clk_hw` links to PLL-derived clocks defined earlier in the file. Consumers use the onecell provider by binding ID.

## Risks
The largest risk is table drift: a wrong register offset, bit index, parent order, or dt-binding ID silently produces incorrect rates or failed peripheral bring-up. `CLK_IGNORE_UNUSED` prevents Linux from disabling shared or firmware-controlled clocks, but overuse can hide missing consumer enables and wastes power. Cross-block parent references assume all relevant provider nodes probe successfully and in a usable order.

## Test Signals
Useful validation is boot probing for every compatible, `/sys/kernel/debug/clk/clk_summary` parent/rate/enabled state, MMC/UART/I2C/SPI/display/GPU/MM functional smoke tests, and suspend/resume checks for clocks marked ignore-unused or shared with AUDCP/DVFS. Binding tests should catch missing compatible strings and clock ID mismatches.
