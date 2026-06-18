## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5260.c

### Purpose
`clk-exynos5260.c` is a multi-CMU Exynos5260 clock provider. Instead of one monolithic initializer, it declares separate `samsung_cmu_info` blocks and `CLK_OF_DECLARE` callbacks for AUD, DISP, EGL, FSYS, G2D, G3D, GSCL, ISP, KFC, MFC, MIF, PERI, and TOP clock-controller nodes.

### Important APIs, Types, and Functions
The file uses Samsung descriptor arrays for each CMU: PLL rate tables `pll2550_24mhz_tbl` and `pll2650_24mhz_tbl`, per-domain `*_clk_regs` save lists, `PNAME()` parent arrays, `*_mux_clks`, `*_div_clks`, `*_gate_clks`, optional `*_pll_clks`, and `*_cmu` descriptors. Each domain initializer is a small function such as `exynos5260_clk_top_init()`, `exynos5260_clk_mif_init()`, or `exynos5260_clk_disp_init()` that calls `samsung_cmu_register_one(np, &domain_cmu)`.

### Control Flow
Device-tree clock-controller nodes with compatible strings like `samsung,exynos5260-clock-top`, `samsung,exynos5260-clock-mif`, and `samsung,exynos5260-clock-peri` are initialized independently during early clock setup. Each call registers the clocks described by that CMU's descriptor. TOP registers fixed PHY clocks, top-level DISP/AUD PLLs, muxes and dividers feeding media, display, bus, peripheral, FSYS, ISP, MFC, G2D, and GSCL domains. MIF registers memory/bus/media PLLs and DDR-related clocks. EGL, KFC, and G3D register local PLLs and CPU/GPU dividers. Leaf domains register user muxes, local dividers, and IP/SCLK gates.

### State and Persistence Behavior
Each `samsung_cmu_info` supplies `.clk_regs` so the shared Samsung CMU code can preserve domain-local CMU registers across suspend or power transitions. The file itself has no runtime function bodies beyond the init callbacks and no heap state. Persistent state is distributed across hardware CMU register banks, including PLL programming, mux parent choices, divider ratios, and IP gate states. Several MIF gates are marked `CLK_IGNORE_UNUSED` because memory, DREX, RTC, monotonic counter, and secure memory clocks must not be disabled by generic cleanup.

### Dependencies and Integration Points
The source depends on `clk-exynos5260.h` for register offsets, `dt-bindings/clock/exynos5260-clk.h` for IDs, and Samsung clock helpers in `clk.h` and `clk-pll.h`. Parent names intentionally cross CMU boundaries: many leaf domains select user clocks produced by TOP, while TOP selects PLL outputs from MIF and top-local PLLs. Consumers include display/HDMI/DP/MIPI, audio, USB/MMC/FSYS, image scaler and camera, ISP, MFC video codec, G2D/JPEG/SSS, G3D, CPU clusters, memory interface, serial peripherals, timers, thermal, RTC, TZPC, and secure key blocks.

### Risks and Test Signals
Cross-CMU parent ordering and parent-name exactness are the largest risks. If TOP or MIF providers are missing or a string is mistyped, later CMUs can register orphaned parents or consumers can defer indefinitely. Register offsets come from the companion header and are repeated across many secure and non-secure gate groups, so copy/paste bit errors are plausible. Test signals include all Exynos5260 clock compatible nodes binding, no unresolved parent warnings, sane clock-summary trees from TOP to leaf domains, working CPU/GPU/storage/display/audio/media devices, suspend/resume of each CMU register bank, and validation that memory-critical MIF gates remain enabled after late init.
