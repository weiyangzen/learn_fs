## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos4.c

### Purpose
`clk-exynos4.c` is the Common Clock Framework provider for Exynos4210, Exynos4212, and Exynos4412 clock controllers. It maps the SoC clock-controller register file into Samsung clock descriptors for PLLs, parent muxes, dividers, gates, fixed-rate clocks, fixed-factor clocks, CPU frequency clocks, and suspend/resume register preservation. Although it lives under the Ceph client source mirror, the code is a Linux ARM SoC clock driver.

### Important APIs, Types, and Functions
The main local state is `reg_base`, the MMIO base for the clock controller, and `exynos4_soc`, which selects 4210 versus 4x12 behavior. Key tables include `exynos4_clk_regs`, `exynos4210_clk_save`, `exynos4x12_clk_save`, `src_mask_suspend`, and `src_mask_suspend_e4210` for sleep handling; `exynos4210_plls` and `exynos4x12_plls`; SoC-shared and SoC-specific mux/div/gate arrays; and `cmu_info_exynos4`, `cmu_info_exynos4210`, and `cmu_info_exynos4x12`.

The important functions are `exynos4_get_xom()`, which reads the chipid XOM bit to infer the external oscillator parent for `fin_pll`; `exynos4_clk_register_finpll()`, which publishes `fin_pll` from either `xxti` or `xusbxti`; `exynos4x12_core_down_clock()`, which programs CPU idle clock-down controls; and `exynos4_clk_init()`, the shared initializer. `exynos4210_clk_init()`, `exynos4212_clk_init()`, and `exynos4412_clk_init()` bind that initializer to device-tree compatible strings via `CLK_OF_DECLARE`.

### Control Flow
At early boot the matching `CLK_OF_DECLARE` callback maps the clock-controller node with `of_iomap()`, creates a `samsung_clk_provider`, registers external fixed oscillators from `samsung,clock-xxti` and `samsung,clock-xusbxti`, derives and registers `fin_pll`, then registers PLLs. Exynos4210 registers `mout_vpllsrc` before PLL registration so VPLL can use the correct parent; Exynos4x12 selects the newer PLL descriptors directly from `fin_pll`.

After PLLs, the shared Exynos4 CMU clocks are registered, then the SoC-specific clocks are layered on. Exynos4210 uses `cmu_info_exynos4210`; Exynos4212 and Exynos4412 use `cmu_info_exynos4x12` and then register the appropriate CPU clock table. Exynos4212/4412 also program PWR_CTRL idle clock-down settings. Finally the driver installs sleep save/restore metadata, adds the OF clock provider, and prints current APLL/MPLL/EPLL/VPLL and ARM clock rates.

### State and Persistence Behavior
The persistent state is hardware clock-controller register state: PLL configuration, mux selections, divider ratios, gate bits, clockout selections, and CPU idle clock controls. The driver itself keeps only static init-time tables and the MMIO base pointer. Suspend handling uses `samsung_clk_extended_sleep_init()` for the common register list and mask/value overrides, plus additional Exynos4210 or Exynos4x12 save sets. The mask override arrays force safe source-mask and PLL values across suspend.

`CLK_IGNORE_UNUSED` is used for clocks such as chipid and sysreg that must remain available even without a visible Linux consumer. CPU clock rate tables encode divider programming for OPP transitions through the Samsung CPU clock helper rather than direct ad hoc register writes.

### Dependencies and Integration Points
The file depends on `dt-bindings/clock/exynos4.h`, Linux OF address mapping, CCF provider APIs, and Samsung helpers from `clk.h` and `clk-cpu.h`. Device tree supplies the clock-controller compatible node, external oscillator nodes, and the chipid node used to read XOM. Downstream consumers include CPU frequency, display, HDMI, camera/FIMC/CSIS, MFC, G3D/G2D, MMC, USB, UART, SPI, I2C, audio, watchdog, RTC, sysreg, and PMU-related blocks.

### Risks and Test Signals
Risks center on table accuracy: clock IDs must match `exynos4.h`, parent strings must match earlier registrations, and bit offsets must match the SoC manual. XOM handling is fragile because it reaches outside the clock controller into chipid space; failure falls back to 24 MHz and can hide board description mistakes. Suspend mask values and `CLK_IGNORE_UNUSED` flags are hardware policy, so changing them can cause resume hangs or late-init clock disable failures. Test signals include boot without unresolved clock providers, sane `/sys/kernel/debug/clk/clk_summary` parent chains, cpufreq transitions for Exynos4210/4212/4412, working UART/MMC/display/camera/audio devices, and system suspend/resume preserving PLL and source-mask state.
