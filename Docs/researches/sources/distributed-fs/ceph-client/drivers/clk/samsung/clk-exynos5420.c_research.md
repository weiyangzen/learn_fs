## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5420.c

### Purpose
`clk-exynos5420.c` registers the shared Exynos5420 and Exynos5800 clock tree. It covers the main Exynos5x CMU, SoC-specific 5420 or 5800 mux/div/gate additions, PLLs, CPU and KFC CPU clocks, memory/CDREX clocks, top bus clocks, media/peripheral clocks, and power-domain sub-CMUs for display, scaler, GPU, MFC, MSCL, and Exynos5800 MAU.

### Important APIs, Types, and Functions
Important state is `reg_base` and `exynos5x_soc`. Main data includes `exynos5x_clk_regs`, `exynos5800_clk_regs`, `exynos5420_set_clksrc`, shared and SoC-specific parent arrays, fixed-rate and fixed-factor arrays, `exynos5x_mux_clks`, `exynos5x_div_clks`, `exynos5x_gate_clks`, `exynos5420_*` and `exynos5800_*` additions, sub-CMU div/gate/suspend arrays, PLL rate tables, `exynos5x_plls`, and CPU clock tables `exynos5420_cpu_clks` and `exynos5800_cpu_clks`. The shared initializer is `exynos5x_clk_init()`, wrapped by `exynos5420_clk_init()` and `exynos5800_clk_init()` through `CLK_OF_DECLARE_DRIVER`.

### Control Flow
Early boot maps the clock-controller node, initializes a Samsung clock provider, registers external `fin_pll`, selects 24 MHz PLL rate tables, chooses the BPLL rate table based on SoC variant, and registers shared PLLs, fixed rates, fixed factors, muxes, dividers, and gates. It then overlays Exynos5420-specific or Exynos5800-specific tables. CPU clocks for ARM and KFC clusters are registered with variant-specific ARM divider tables. The driver installs extended sleep handling with `exynos5420_set_clksrc`, adds Exynos5800 extra sleep registers if needed, and initializes sub-CMUs for power-domain controlled blocks.

Before publishing the OF provider, the driver permanently enables the top G3D mux path and the BPLL mux path with `clk_prepare_enable()` to keep internal G3D buses and DRAM operation stable regardless of consumer-managed gates.

### State and Persistence Behavior
Hardware persistence is extensive: PLL controls, top mux trees, CPU/KFC dividers, CDREX memory clocks, source masks, bus and IP gates, ISP sensor/SPI/UART clocks, display clocks, and power-domain-local gate/divider state. `samsung_clk_extended_sleep_init()` saves the main register set and writes safe source-mask/gate values from `exynos5420_set_clksrc`. Sub-CMU descriptors save and restore masked state for DISP, GSC, G3D, MFC, MSC, and MAU on runtime power-domain transitions.

Flags such as `CLK_IS_CRITICAL`, `CLK_IGNORE_UNUSED`, `CLK_SET_RATE_PARENT`, `CLK_RECALC_NEW_RATES`, and `CLK_GET_RATE_NOCACHE` encode operational constraints. CDREX dividers intentionally share register bits and use no-cache rate reads to reflect hardware coupling between bus and DREX interfaces.

### Dependencies and Integration Points
The file depends on `dt-bindings/clock/exynos5420.h`, OF mapping, Linux CCF, Samsung `clk.h`, `clk-cpu.h`, and `clk-exynos5-subcmu.h`. Consumers span CPU frequency for ARM/KFC clusters, DRAM/CDREX, G3D, display/HDMI/DP/MIPI, camera/GSCL/ISP, MFC/MSCL/JPEG/G2D, FSYS USB/MMC/UFS/Unipro, UART/I2C/SPI/audio/PWM, timers, watchdog, RTC, TMU, secure-world and sysreg blocks, and power-domain controllers identified by labels.

### Risks and Test Signals
Risks include SoC-variant drift between Exynos5420, Exynos5422-like BPLL behavior, and Exynos5800 camera/MAU additions; cross-domain parent-string mistakes; changing critical clock flags; incorrect suspend mask constants; and missing sub-CMU power-domain labels causing clocks to stay deferred. The explicit `clk_prepare_enable()` calls are stability requirements and should not be removed without DRAM and GPU bus validation. Test signals include booting both 5420 and 5800 compatible variants, correct ARM/KFC cpufreq transitions, stable DRAM under memory stress, working display/media/GPU/storage/peripherals, all expected sub-CMU devices resolving deferred gates, and reliable runtime and system suspend/resume.
