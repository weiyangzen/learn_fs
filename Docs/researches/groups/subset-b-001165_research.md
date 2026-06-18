# subset-b-001165 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos4.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos4412-isp.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos4412-isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5-subcmu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5-subcmu.c

### Purpose
`clk-exynos5-subcmu.c` implements the shared support layer for Exynos5 clocks that belong to independently power-managed sub-CMUs. Main `CLK_OF_DECLARE` clock drivers call it early to defer power-domain gate clock lookups, save safe register values, and later create per-power-domain platform devices that register the real divider and gate clocks under runtime PM.

### Important APIs, Types, and Functions
The public entry point is `exynos5_subcmus_init(struct samsung_clk_provider *ctx, int nr_cmus, const struct exynos5_subcmu_info **cmu)`. Local static state stores the main provider `ctx`, the sub-CMU info array `cmu`, and `nr_cmus`. Internal helpers are `exynos5_subcmu_clk_save()`, `exynos5_subcmu_clk_restore()`, `exynos5_subcmu_defer_gate()`, `exynos5_subcmu_probe()`, `exynos5_clk_register_subcmu()`, and `exynos5_clk_probe()`.

### Control Flow
The main SoC clock driver calls `exynos5_subcmus_init()` during early clock setup. For each sub-CMU, the helper installs `ERR_PTR(-EPROBE_DEFER)` lookups for each gate ID so early consumers defer instead of seeing missing clocks, and saves the specified register fields while writing safe suspend values.

At `core_initcall`, this file registers two platform drivers. The `exynos5-clock` driver binds to the same top-level clock-controller compatible nodes as the early clock driver after OF platform population. Its probe scans compatible power-domain nodes `samsung,exynos4210-pd`, compares their `label` strings against each sub-CMU `pd_name`, and allocates an `exynos5-subcmu` platform device for each match. The sub-CMU device is attached to the generic PM domain with `of_genpd_add_device()`.

When an `exynos5-subcmu` device probes, it enables runtime PM, takes a runtime PM reference, temporarily assigns `ctx->dev` so clock registration is associated with the sub-CMU device, registers sub-CMU dividers and gates, clears `ctx->dev`, and drops the runtime PM reference. Runtime suspend and resume save or restore the masked register set under `ctx->lock`.

### State and Persistence Behavior
The file uses module-static globals rather than per-SoC objects, so it assumes one active Exynos5 clock provider instance. Each `exynos5_subcmu_reg_dump` stores an offset, a value to program for suspend, a mask of controlled bits, and the saved masked value. Save writes `(old & ~mask) | value` then records `old & mask`; restore writes the saved masked bits back while preserving bits outside the mask.

### Dependencies and Integration Points
Dependencies include Samsung clock provider internals, runtime PM, generic PM domains, OF node scanning, and platform devices. It is consumed by Exynos5250 and Exynos5420/5800 clock drivers in this subset. It integrates with power-domain labels such as `DISP1`, `DISP`, `GSC`, `G3D`, `MFC`, `MSC`, and `MAU`.

### Risks and Test Signals
Risks include reliance on global state, label-string matching rather than direct phandles, unchecked `of_genpd_add_device()` return, and lack of cleanup if platform-device add fails after genpd attachment. The deferred lookup mechanism depends on later registration using the same clock IDs. Test signals include power-domain child devices being created for all expected labels, early consumers deferring then probing after sub-CMU registration, runtime PM save/restore under lock, and suspend/resume preserving clocks in display, scaler, GPU, MFC, and MAU domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5-subcmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5-subcmu.h -->
## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5-subcmu.h

### Purpose
`clk-exynos5-subcmu.h` defines the small contract between Exynos5 SoC clock drivers and the shared sub-CMU runtime-PM helper in `clk-exynos5-subcmu.c`.

### Important APIs, Types, and Functions
`struct exynos5_subcmu_reg_dump` describes one masked register save/restore entry: `offset`, suspend `value`, bit `mask`, and runtime `save` storage. `struct exynos5_subcmu_info` describes one power-domain sub-CMU: divider clock array, gate clock array, suspend register dump array, and the power-domain `pd_name` label used to match a DT power domain. The header declares `exynos5_subcmus_init()`.

### Control Flow
The header has no executable control flow. SoC files instantiate `struct exynos5_subcmu_info` arrays and pass them to `exynos5_subcmus_init()` after main CMU clocks are registered. The implementation then defers gate lookups, creates platform devices for matching power domains, and registers the real sub-CMU clocks at runtime.

### State and Persistence Behavior
The `save` field in `struct exynos5_subcmu_reg_dump` is mutable state owned by the sub-CMU helper. The `value` and `mask` fields encode the low-power hardware policy, while `offset` ties that policy to the main clock-controller MMIO base. `struct exynos5_subcmu_info` instances are usually static data in SoC clock drivers, but their `suspend_regs` entries are modified at runtime.

### Dependencies and Integration Points
The header depends on type declarations from the Samsung clock framework, especially `struct samsung_clk_provider`, `struct samsung_div_clock`, and `struct samsung_gate_clock`, which are available because including C files include `clk.h` before this header. It integrates Exynos5250 and Exynos5420/5800 SoC-specific tables with the generic sub-CMU helper.

### Risks and Test Signals
The main risk is ABI-like coupling between table initializers and helper expectations: `pd_name` must match device-tree power-domain labels, register masks must not cover unrelated bits, and `suspend_regs` must be writable because `save` is updated. Build coverage catches missing type definitions and initializer drift. Runtime test signals come from the C helper: expected power-domain sub-CMU devices, deferred clock resolution, and suspend/resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5-subcmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5250.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5260.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5260.h -->
## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5260.h

### Purpose
`clk-exynos5260.h` defines Exynos5260 CMU register offsets used by `clk-exynos5260.c`. It is the hardware register map layer for AUD, DISP, EGL, FSYS, G2D, G3D, GSCL, ISP, KFC, MFC, MIF, PERI, and TOP clock management units.

### Important APIs, Types, and Functions
The header exports preprocessor constants only. Register groups follow a consistent naming scheme: `MUX_SEL_*`, `MUX_ENABLE_*`, `MUX_STAT_*`, `MUX_IGNORE_*`, `DIV_*`, `DIV_STAT_*`, `EN_ACLK_*`, `EN_PCLK_*`, `EN_SCLK_*`, `EN_IP_*`, PLL lock/control/frequency-detect registers, clockout registers, and a few domain-specific power/EMA/DDR controls such as `PWR_CTRL`, `ARMCLK_STOPCTRL`, `DREX_FREQ_CTRL`, and `DDRPHY_LOCK_CTRL`.

### Control Flow
There is no executable control flow. The C file includes this header and uses the offsets to build `clk_regs` save lists and mux/div/gate/PLL descriptors. The shared Samsung CCF implementation then performs actual MMIO operations using these offsets relative to each CMU node's mapped base.

### State and Persistence Behavior
The constants describe persistent hardware state, not software state. Offsets select registers that hold parent mux selections, enabled mux paths, divider ratios, divider status, secure and non-secure gate bits, PLL configuration, memory-controller timing controls, and clockout status. Because they are used in suspend save lists, any incorrect value can corrupt preservation of a whole CMU bank.

### Dependencies and Integration Points
The header is tightly coupled to `clk-exynos5260.c` and the Exynos5260 binding header. Its register names align with clock descriptor names and clock IDs used by device-tree consumers. The grouping also documents the hardware-domain boundaries that the device tree must represent as separate clock-controller nodes.

### Risks and Test Signals
Risks are mostly maintenance risks: wrong offsets compile cleanly but write the wrong hardware register, uppercase/lowercase inconsistency can invite duplicate definitions, and secure register groups are easy to confuse with ordinary gate groups. Build tests catch missing macro names, while runtime tests require domain-by-domain clock enable, rate changes, and suspend/resume. `clk_summary` plus functional tests for display, audio, FSYS, media, CPU, GPU, and memory interface are the practical signals that the register map is coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5260.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5410.c -->
## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5410.c

### Purpose
`clk-exynos5410.c` is a compact Exynos5410 clock-controller provider. It registers a subset of CPU/KFC, PLL, FSYS, PERIC, PERIS, G2D, and top-level bus clocks needed for this SoC through one `samsung_cmu_info`.

### Important APIs, Types, and Functions
The key data is `exynos5410_plls`, `exynos5410_mux_clks`, `exynos5410_div_clks`, `exynos5410_gate_clks`, and the aggregate `cmu`. Parent arrays describe APLL/BPLL/CPLL/EPLL/MPLL/KPLL roots, CPU and KFC muxing, MPLL/BPLL user paths, FSYS MMC/USB parents, UART/PWM parents, and top ACLK parents. The only initializer is `exynos5410_clk_init()`, registered with `CLK_OF_DECLARE`.

### Control Flow
At early boot, `exynos5410_clk_init()` reads the first clock from the clock-controller node with `of_clk_get()`. If it is present and runs at 24 MHz, the EPLL descriptor receives the `exynos5410_pll2550x_24mhz_tbl` rate table. The function then calls `samsung_cmu_register_one(np, &cmu)` to register PLLs, muxes, dividers, and gates in one pass, and emits a debug completion message.

### State and Persistence Behavior
The file itself stores no dynamic state. Hardware state includes PLL controls, CPU/KFC source selection and dividers, FSYS MMC/USB dividers, peripheral UART/PWM dividers, and gates for MMC, USB, DMA, UART/I2C/USI/SPI/PWM, timers, watchdog, RTC, TMU, SSS, and a few serial clocks. This file does not declare explicit sleep register lists, so persistence is whatever the generic CMU path provides for this simple registration.

### Dependencies and Integration Points
The file depends on `dt-bindings/clock/exynos5410.h`, Linux CCF, and Samsung `clk.h`. It integrates with consumers for CPU/KFC clocks, eMMC/SD, USB host/device, DMA, UART, I2C, SPI-like USI blocks, timers, watchdog, RTC, thermal, and security. It uses `CLKS_NR` of 512 rather than a last-ID expression, so the binding ID range must remain within that capacity.

### Risks and Test Signals
The code is sparse and table-driven; risks include missing clocks compared with hardware needs, incorrect parent names such as `aclk200_fsys` if no provider creates them, and `DIV(0, "aclk266", "mpll_user_p", ...)` appearing to reference a parent string that looks like a parent-array symbol rather than a registered clock name. Test signals include clean boot without unresolved parents, functional MMC/USB/UART/I2C/timer/watchdog devices, EPLL rates only exposed when the input is 24 MHz, and clock-summary validation for CPU, KFC, FSYS, and PERIC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5420.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5420.c -->
