# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.c

## Purpose
This is the top-level CV1800/CV1810/SG2000 clock controller driver. It declares the complete clock topology for the CV18xx family using the reusable CV18xx PLL/IP clock classes, performs SoC-specific pre-initialization, registers each `clk_hw`, and publishes an OF onecell provider.

## Important APIs, Types, And Functions
Local descriptor types are `struct cv1800_clk_desc` and `struct cv1800_clk_ctrl`. The descriptor selects the onecell table and optional `pre_init()` hook for each compatible. `CV1800_DIV_FLAG` standardizes one-based, round-closest dividers. The file uses clock-construction macros from `clk-cv18xx-ip.h` and `clk-cv18xx-pll.h`: `CV1800_INTEGRAL_PLL`, `CV1800_FACTIONAL_PLL`, `CV1800_GATE`, `CV1800_DIV`, `CV1800_BYPASS_DIV`, `CV1800_FIXED_DIV`, `CV1800_BYPASS_FIXED_DIV`, `CV1800_MUX`, `CV1800_BYPASS_MUX`, `CV1800_MMUX`, and `CV1800_ACLK`.

Key functions are `cv18xx_clk_disable_auto_pd()`, `cv18xx_clk_disable_a53()`, `cv1800_pre_init()`, `cv1810_pre_init()`, `sg2000_pre_init()`, `cv1800_clk_init_ctrl()`, and `cv1800_clk_probe()`. Matching compatibles are `sophgo,cv1800-clk`, `sophgo,cv1800b-clk`, `sophgo,cv1810-clk`, `sophgo,cv1812h-clk`, and `sophgo,sg2000-clk`.

## Control Flow
Probe maps MMIO resource 0, retrieves match data, allocates a controller, runs descriptor-specific pre-init, then calls `cv1800_clk_init_ctrl()`. Registration walks the selected `clk_hw_onecell_data` array, skips NULL entries, initializes each clock's shared base and lock through `hw_to_cv1800_clk_common()`, and registers the hardware object with `devm_clk_hw_register()`. Finally it installs `devm_of_clk_add_hw_provider()`.

The topology begins with oscillator parents and PLLs: FPLL and MIPIMPLL as integral PLLs, and MPLL/TPLL/A0PLL/DISPPLL/CAM0PLL/CAM1PLL as fractional PLLs with synthesizer controls. Downstream clocks define TPU, AXI4/AXI6, timers, RTC, storage, GPIO, Ethernet, audio, SDMA, SPI, UART, I2C, USB, VIP, camera outputs, video codec, PWM, C906, and A53 clocks. `cv1800_hw_clks` is smaller and excludes unsupported `CLK_DISP_SRC_VIP`; `cv1810_hw_clks` includes it and is reused for SG2000.

## State And Persistence
The clock tree is represented by static global `clk_hw` objects. Probe writes runtime state into each `cv1800_clk_common` (`base` and shared spinlock pointer). Hardware state lives in clock-enable, divider, mux, bypass, PLL, and synthesizer registers. Pre-init permanently adjusts hardware state for the running boot: CV1800 disables unsupported display source VIP, CV1800/CV1810 force A53-related bypass to avoid hangs on variants where A53 is unused, and all variants disable PLL auto power-down fields.

## Dependencies And Integration Points
The file depends on CV1800 register offsets and clock ID limits from `clk-cv1800.h`, common bit helpers from `clk-cv18xx-common.h`, IP clock ops from `clk-cv18xx-ip.h`, PLL ops from `clk-cv18xx-pll.h`, and dt-bindings in `sophgo,cv1800.h`. It integrates with platform probing, Device Tree match data, CCF parent-data resolution, and downstream IP consumers requesting binding IDs.

## Risks
This file is table-heavy; a wrong register, bit shift, parent list, or onecell index can break a whole subsystem without compile-time detection. Some clocks are marked `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED`; those policy choices need hardware validation because overuse hides unused-clock bugs while underuse can hang boot. The comment on A53 states bypass must not be disabled on CV180x/CV181x or the SoC hangs, so parent/rate changes on `clk_a53` are particularly dangerous. The Ethernet 500M clocks appear to use `REG_DIV_CLK_GPIO_DB` rather than the nearby Ethernet-specific register defines, which should be checked against the TRM.

## Test Signals
Boot each compatible and inspect `clk_summary` for parent/rate correctness. Exercise `clk_set_rate()` and `clk_set_parent()` for storage, UART, I2C, audio, video, and C906/A53 paths. Verify pre-init register writes with early debug reads. Tests should include suspend/resume or late unused-clock disabling to ensure critical and ignore-unused flags are correct.
