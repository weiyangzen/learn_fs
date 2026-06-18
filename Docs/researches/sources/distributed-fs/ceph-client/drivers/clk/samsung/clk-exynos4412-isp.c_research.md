## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos4412-isp.c

### Purpose
`clk-exynos4412-isp.c` provides the Exynos4x12 ISP power-domain clock controller as a normal platform driver. It registers the local ISP divider and gate clocks for FIMC ISP, DRC, FD, FIMC Lite, MCU ISP, SMMUs, ISP-local serial/peripheral blocks, and supporting performance monitors.

### Important APIs, Types, and Functions
The file uses `struct samsung_div_clock`, `struct samsung_gate_clock`, and `struct samsung_clk_reg_dump`. `exynos4x12_clk_isp_save` lists the ISP-domain registers to preserve, and `exynos4x12_save_isp` stores the allocated dump buffer. The principal functions are `exynos4x12_isp_clk_probe()`, runtime PM callbacks `exynos4x12_isp_clk_suspend()` and `exynos4x12_isp_clk_resume()`, and the `core_initcall()` registration function `exynos4x12_isp_clk_init()`.

### Control Flow
The platform driver binds to `samsung,exynos4412-isp-clock`. Probe maps resource 0 with `devm_platform_ioremap_resource()`, allocates a register dump buffer, initializes a Samsung clock provider sized by `CLKS_NR_ISP`, stores it as driver data, marks runtime PM active, enables runtime PM, and takes a runtime PM reference so the ISP power domain is on while clocks are registered. It then registers divider clocks, registers gate clocks, publishes the OF provider, and drops the runtime PM reference.

Runtime suspend saves ISP divider and gate registers using the provider's `reg_base`; runtime resume restores them. Late system sleep is delegated through `pm_runtime_force_suspend()` and `pm_runtime_force_resume()`, so the same runtime PM logic handles system suspend transitions.

### State and Persistence Behavior
The driver allocates one global register-save buffer and stores the clock provider in platform driver data. Long-lived hardware state consists of ISP divider ratios and gate bits inside the ISP power domain. Because the ISP domain can be power-gated independently, the driver saves and restores its local CMU state whenever runtime PM suspends or resumes the domain.

### Dependencies and Integration Points
Dependencies include `dt-bindings/clock/exynos4.h`, platform devices, OF matching, runtime PM, and Samsung clock helpers from `clk.h`. The file integrates with the Exynos4412 ISP power domain and exports clocks to ISP-related media drivers through the device-tree clock provider. It also relies on parent clocks such as `aclk200` and `aclk400_mcuisp` being registered by the main Exynos4 clock driver.

### Risks and Test Signals
Risks include registering clocks while the ISP domain is off, missing parent clocks from the main CMU, incorrect `CLKS_NR_ISP`, and global save-buffer lifetime if multiple matching devices ever appeared. Runtime PM error handling is minimal: `pm_runtime_get_sync()` return value is not checked. Test signals include successful probe of `samsung,exynos4412-isp-clock`, no deferred clock consumers for ISP/FIMC devices, runtime suspend/resume preserving gate states, system suspend/resume of ISP media workloads, and `clk_summary` showing ISP clocks under the expected parent paths.
