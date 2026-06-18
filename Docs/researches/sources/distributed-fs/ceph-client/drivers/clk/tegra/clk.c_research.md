# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.c

## Purpose
This file is the shared Tegra clock-provider core used by SoC-specific CAR drivers. It owns the global clock array, peripheral enable reference counts, reset-controller registration, common peripheral enable/reset suspend context, init-table application, clkdev alias registration, special reset dispatch, optional clock-device creation for runtime PM, and the global `tegra_cpu_car_ops` pointer used by CPU power/control code.

## Important APIs, Types, And Functions
Important exported/shared functions include `tegra_clk_init()`, `tegra_add_of_provider()`, `tegra_init_special_resets()`, `tegra_register_devclks()`, `tegra_lookup_dt_id()`, `tegra_clk_dev_register()`, `tegra_init_dup_clks()`, `tegra_init_from_table()`, `tegra_clk_periph_suspend()`, `tegra_clk_periph_resume()`, `tegra_clk_set_pllp_out_cpu()`, and `get_reg_bank()`. Reset-controller callbacks are `tegra_clk_rst_assert()`, `tegra_clk_rst_deassert()`, and `tegra_clk_rst_reset()`.

Key global state includes `tegra_car_np`, `tegra_cpu_car_ops`, `periph_clk_enb_refcnt`, `periph_banks`, `periph_state_ctx`, `clks`, `clk_num`, `clk_data`, `clk_base`, and special reset callback pointers. `periph_regs[]` describes each CAR peripheral bank's enable and reset register offsets.

## Control Flow
SoC drivers call `tegra_clk_init(regs, num, banks)` early to set the CAR base, allocate per-clock and per-enable reference arrays, record bank count, and allocate suspend context when PM sleep is enabled. They register clocks into the returned `clks` array and finally call `tegra_add_of_provider()`, which normalizes missing clocks to `ERR_PTR(-EINVAL)`, publishes an OF onecell provider, and registers a reset controller with reset count equal to common peripheral reset lines plus any SoC-specific special resets.

Reset assert/deassert first handle common banked reset IDs by writing set/clear registers. IDs after the banked range dispatch to SoC-specific special reset handlers installed by `tegra_init_special_resets()`. `tegra_init_from_table()` applies parent, rate, and enable state rows from SoC init tables. `arch_initcall(tegra_clocks_apply_init_table)` invokes a SoC-assigned callback late enough to apply table state after the SoC driver has assigned it.

## State And Persistence Behavior
The file persists clock pointers for OF and clkdev lookup, peripheral enable reference counts used by gate implementations, banked peripheral enable/reset snapshots for suspend/resume, reset-controller configuration, and special reset callbacks. Suspend saves each bank's enable registers followed by reset registers. Resume writes enables first, waits for reset propagation, restores reset registers, and fences again.

`tegra_clk_dev_register()` can create a platform device for a clock subnode under the CAR node, enable runtime PM on that device, and register the clock against that device. This makes some clock implementations runtime-PM aware while keeping early boot clocks device-less.

## Dependencies And Integration Points
The file integrates Linux CCF, clkdev, OF clock providers, reset-controller framework, platform devices, runtime PM, Tegra fuse/chipid APB flush behavior, and SoC-specific files such as Tegra20/30/210 CAR drivers. It is the shared contract behind the `clks[]` arrays populated from dt-binding IDs and the reset specifiers consumed by device tree clients.

## Risks
The module uses global singleton state, so only one Tegra CAR instance is expected. `tegra_clk_rst_assert()` always reads chip ID to flush APB before asserting reset; that is conservative but means reset behavior depends on fuse/chipid access being safe. Missing clocks are converted to `ERR_PTR(-EINVAL)`, and init-table rows warn but continue, so incomplete clock registration can appear as later consumer failures. `tegra_clk_dev_register()` relies on child node names derived by replacing underscores with hyphens in clock names, making DT naming part of the API. Special reset IDs must stay aligned between bank counts, `num_special_reset`, and SoC reset bindings.

## Test Signals
Signals include onecell provider registration with the expected `clk_num`, reset-controller registration with expected reset count, successful common and special reset operations, correct suspend/resume restoration of peripheral enable/reset state, correct clkdev lookup for legacy aliases, runtime-PM device creation for clocks with matching child DT nodes, and init-table warnings staying absent during boot.
