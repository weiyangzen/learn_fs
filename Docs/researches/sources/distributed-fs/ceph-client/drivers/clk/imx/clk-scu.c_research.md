# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.c

## Purpose
Provides the SCU-backed clock implementation for i.MX8 SCFW platforms. It turns clock registrations into platform devices, attaches power domains, performs SCU PM/MISC RPCs for rate/parent/enable/GPR operations, and saves/restores clock state across system sleep.

## Important APIs, Types, And Functions
Key types are `struct imx_scu_clk_node`, `struct clk_scu`, and `struct clk_gpr_scu`. Public entry points include `imx_clk_scu_module_init()`, `imx_clk_scu_module_exit()`, `imx_clk_scu_init()`, `imx_scu_of_clk_src_get()`, `imx_clk_scu_alloc_dev()`, `__imx_clk_scu()`, `imx_clk_scu_unregister()`, and `__imx_clk_gpr_scu()`. Clock ops call SCFW RPCs through `clk_scu_recalc_rate()`, `clk_scu_set_rate()`, `clk_scu_get_parent()`, `clk_scu_set_parent()`, and `sc_pm_clock_enable()`. CPU rate changes use `clk_scu_atf_set_cpu_rate()` and ARM SMCCC.

## Control Flow
`imx_clk_scu_init()` gets the SCU IPC handle, initializes per-resource clock lists for two-cell providers, finds the SCU power-domain node, and stores an optional resource allowlist. Clock declarations call `imx_clk_scu_alloc_dev()`, which validates the resource, checks SCFW ownership, creates a platform device forced to bind `imx-scu-clk`, attaches a genpd unless it is an A-core resource, and adds the device. `imx_clk_scu_probe()` enables runtime PM for non-CPU clocks, registers the actual `clk_hw`, appends it to `imx_scu_clks[resource]`, and autosuspends.

## State And Persistence Behavior
Persistent clock authority is SCFW. Linux stores IPC handle, power-domain node, resource table, per-resource lists, and per-clock saved parent/rate/enabled state for noirq sleep. Resume restores parent, rate, and enabled state except CPU clocks and PI PLL enable.

## Dependencies And Integration Points
Depends on SCU IPC, SCFW RM ownership API, PM domain framework, runtime PM, ARM SMCCC for CPU frequency, Xen headers, OF clock providers, and resource constants. Higher-level i.MX8QXP/QM code uses the inline wrappers in `clk-scu.h`.

## Risks
Resource allowlists must be sorted. `imx_clk_scu_alloc_dev()` returns `NULL` for successful deferred platform-device creation and also for unowned resources, so callers intentionally ignore return values. Sleep restore order must respect power domains and SCFW ownership. CPU clocks are special because SCFW may report them unowned while Linux still controls cpufreq via ATF.

## Test Signals
Boot SCU platforms with two-cell clock providers, verify phandle lookups by resource/type, cpufreq changes via SMCCC, runtime PM autosuspend, suspend/resume restore for parent/rate/enabled clocks, and resource partition tests where unowned clocks are skipped.
