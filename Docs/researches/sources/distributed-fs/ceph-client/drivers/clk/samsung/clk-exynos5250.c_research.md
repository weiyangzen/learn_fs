## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5250.c

### Purpose
`clk-exynos5250.c` registers the Exynos5250 SoC clock tree. It covers CPU, core, TOP, GSCL, display, MAU, FSYS, GEN, PERIC, PERIS, CDREX, ACP, ISP, PLL, CPU clock, and display sub-CMU clocks using Linux CCF and Samsung clock helpers.

### Important APIs, Types, and Functions
Important data includes `exynos5250_clk_regs`, parent `PNAME()` arrays, `exynos5250_pll_pmux_clks`, `exynos5250_mux_clks`, `exynos5250_div_clks`, `exynos5250_gate_clks`, `exynos5250_disp_gate_clks`, `exynos5250_disp_suspend_regs`, PLL rate tables for 24 MHz inputs, `exynos5250_plls`, and `exynos5250_cpu_clks`. The initializer is `exynos5250_clk_init()`, registered with `CLK_OF_DECLARE_DRIVER`.

### Control Flow
Early boot maps the clock-controller node, creates a `samsung_clk_provider`, registers `fin_pll` from external `samsung,clock-xxti`, registers an early VPLL source mux, selects PLL rate tables when the input clocks are 24 MHz, then registers PLLs, fixed-rate clocks, fixed-factor clocks, muxes, dividers, gates, and the CPU clock. It programs PWR_CTRL1 for ARM clock-down during WFI/WFE and PWR_CTRL2 for clock-up on idle exit. It then registers sleep save/restore metadata and initializes the DISP1 sub-CMU support so display power-domain gates are deferred until the display domain device is available.

### State and Persistence Behavior
Persistent state is the Exynos5250 CMU register file: PLL controls, muxes, dividers, gate bits, source masks, PWR_CTRL idle policy, CDREX source selection, and PLL div2 selection. The file saves all listed registers with `samsung_clk_sleep_init()`. The DISP1 sub-CMU uses `exynos5_subcmu_reg_dump` entries to force `GATE_IP_DISP1` on and safe `SRC_TOP3` mux selections while saving the original masked values.

### Dependencies and Integration Points
The file depends on `dt-bindings/clock/exynos5250.h`, OF mapping, Samsung CCF helpers, CPU clock helpers, and the Exynos5 sub-CMU helper. Consumers include CPU frequency, display and HDMI/DP, GSCL/camera, MFC, G3D, rotator/JPEG/MDMA, storage, USB/SATA/MIPI HSI, UART/I2C/SPI/audio/PWM, watchdog, RTC, TMU, PMU, sysreg, and TrustZone peripheral clocks.

### Risks and Test Signals
Risks include incorrect 24 MHz assumptions, rate-table omissions for non-24 MHz boards, bit-position mistakes in large sorted tables, and PM instability if PWR_CTRL or DISP1 sub-CMU masks are changed. Some clock gates are in power domains, so exposing them before genpd is active would break consumers; the sub-CMU defer path is critical. Test signals include booting with all clock providers resolved, `armclk` rate matching CPU OPPs, working display after DISP1 power cycling, functional MMC/USB/SATA/UART/I2C/SPI/audio blocks, and system suspend/resume preserving CMU state.
