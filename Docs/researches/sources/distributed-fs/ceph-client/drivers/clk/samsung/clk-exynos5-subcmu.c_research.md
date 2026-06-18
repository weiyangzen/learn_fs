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
