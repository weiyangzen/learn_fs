# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.c

## Purpose

`clk-cpu.c` implements Samsung Exynos CPU-clock registration and coordinated CPU-domain rate switching for the common clock framework. A CPU clock is exposed as a `clk_hw` whose visible rate equals the primary parent PLL rate, while auxiliary CPU-domain muxes and dividers are reprogrammed around PLL changes so CPU, debug, AXI, ATCLK, PCLKDBG, and related clocks remain safe.

Supported layouts include Exynos4210-style, Exynos5433-style, and Exynos850 cluster 0/cluster 1 style register maps. SoC clock drivers provide `struct samsung_cpu_clock` descriptors and parent-rate-specific divider tables.

## Important APIs, types, and functions

- `struct exynos_cpuclk_regs` stores register offsets for muxes, divider registers, divider status, and Exynos850-style mux/div registers.
- `struct exynos_cpuclk_chip` binds a layout to pre-rate and post-rate callbacks.
- `struct exynos_cpuclk` stores the CCF hardware object, alternate parent, MMIO base, shared lock, copied config table, parent notifier, flags, and chip data.
- `wait_until_divider_stable()` and `wait_until_mux_stable()` poll hardware status with timeout logging.
- `exynos_set_safe_div()` programs temporary safe divider values.
- `exynos_cpuclk_pre_rate_change()` / `exynos_cpuclk_post_rate_change()` handle Exynos 3/4/5 transitions.
- `exynos5433_cpuclk_pre_rate_change()` / `exynos5433_cpuclk_post_rate_change()` handle the Exynos5433 mux layout.
- `exynos850_alt_parent_set_max_rate()`, `exynos850_cpuclk_pre_rate_change()`, and `exynos850_cpuclk_post_rate_change()` implement the Exynos850 alternate-parent divider strategy.
- `exynos_cpuclk_notifier_cb()` dispatches parent PLL notifier events.
- `samsung_clk_register_cpu()` is the public registration loop.

## Control flow

Registration starts in `samsung_clk_register_cpu()`, which calls `exynos_register_cpu_clock()` for each platform descriptor. The helper resolves primary and alternate parent `clk_hw` objects, allocates state, fills `clk_init_data` with `CLK_SET_RATE_PARENT`, registers a parent notifier, copies the zero-terminated divider config table, registers the CPU `clk_hw`, and adds the lookup.

Rate changes propagate from the CPU clock to the primary parent PLL. The parent emits notifier events. On `PRE_RATE_CHANGE`, the layout callback finds the config row whose `prate * 1000` matches the new PLL rate. If needed, it applies a safe divider, switches to the alternate parent, and writes target auxiliary dividers while the PLL is reprogrammed. On `POST_RATE_CHANGE`, it switches back to the primary PLL and removes temporary dividers.

Exynos4210 optionally handles DIV1 and debug/ATB alternate divider workarounds. Exynos5433 uses a different mux bit/status layout and programs DIV0/DIV1. Exynos850 skips transitions to or from the 26 MHz oscillator, constrains the alternate parent through an upstream CMU_TOP divider, switches muxes, writes four divider registers, then restores the alternate parent to maximum rate.

## State and persistence behavior

Each registered CPU clock persists as an allocated `struct exynos_cpuclk` plus a copied config table and parent notifier. There is no unregister path, which matches built-in SoC clock lifetime. Hardware divider and mux state persists in registers until later rate changes or power-management code. Register updates are serialized with the Samsung provider spinlock and IRQ save/restore.

Poll timeouts are logged but not returned as transition failures. Config lookup failures return `-EINVAL`, which is converted to a notifier error.

## Dependencies

The file depends on Samsung provider types and `struct samsung_cpu_clock` from `clk.h`, definitions from `clk-cpu.h`, Linux CCF APIs, notifier APIs, MMIO accessors, spinlocks, jiffies timing, and parent clocks that support notifiers/rate changes. Platform descriptors must supply valid parent IDs, alternate parent IDs, base offsets, layout enums, flags, and zero-terminated `exynos_cpuclk_cfg_data` arrays with `prate` in KHz.

## Risks and edge cases

- Missing config rows reject transitions; missing zero sentinels can overrun arrays.
- `WARN_ON(alt_div >= MAX_DIV)` does not prevent writing the computed divider value.
- Stabilization timeouts only log, so CCF can believe a transition completed even if hardware did not settle.
- Exynos850 calls `clk_set_rate()` on an alternate parent from a PLL notifier path, so parent graph and locking must avoid recursion/deadlock.
- CCF-visible CPU rate equals parent PLL rate despite temporary hardware divider use.

## Test signals

Tests should boot platforms for each layout, run CPU frequency transitions across all configured rates, and check for notifier errors, divider/mux timeout logs, and instability. `clk_summary` should show CPU clocks matching parent PLL rates. Stress should include up/down transitions, alternate-parent faster-than-old-parent cases, Exynos4210 debug divider behavior, Exynos5433 DIV1 programming, and Exynos850 oscillator/alternate-divider paths.
