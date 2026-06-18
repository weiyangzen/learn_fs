# sources/distributed-fs/ceph-client/drivers/clk/clk-sp7021.c

Purpose: platform CCF driver for the Sunplus SP7021 clock controller. It registers PLLs, derived PLL outputs, and a table of gate clocks backed by memory-mapped clock/pll/system registers.

Important APIs/types/functions: `struct sp_pll` wraps a PLL `clk_hw`, register pointer, lock, divider layout, power/bypass bits, base rate, and saved special PLL parameters. `sp_pll_ops` supports enable/disable/is_enabled/determine_rate/recalc_rate/set_rate for bypass-capable PLLs, while `sp_pll_sub_ops` exposes fixed derived PLL outputs. PLL-specific helpers include `plltv_integer_div()`, `plltv_fractional_div()`, `plltv_set_rate()`, `plla_round_rate()`, `plla_set_rate()`, `sp_pll_calc_div()`, and `sp_pll_register()`. Gate metadata is in `sp_clk_gates`.

Control flow: `sp7021_clk_probe()` maps three MMIO resources, writes a default enable mask table to clock-gate registers, allocates onecell clock data, registers PLLA/PLLE/PLLF/PLLTV/PLLSYS and PLLE subclocks, registers PLLTV_A divider, then iterates `sp_clk_gates` to register hiword-mask gates with either external clock or system PLL parents. It registers an OF onecell provider. Runtime PLL callbacks compute bypass, integer/fractional PLLTV settings, lookup PLLA table rates, write hiword-mask fields under spinlock, and read back rates from registers.

State and persistence: state lives in MMIO registers and saved PLL parameter arrays used after determine_rate for special PLL set_rate paths. The driver writes default gate-enable values during probe, which mutates hardware before consumers request clocks. Per-PLL spinlocks protect local register writes, but gate writes use CCF gate helper behavior.

Dependencies and integration: depends on platform resources, `dt-bindings/clock/sunplus,sp7021-clkc.h`, MMIO, bitfield/hiword-mask helpers, CCF onecell provider, and compatible `sunplus,sp7021-clkc`. Consumers use numeric binding IDs up to `CLK_MAX`.

Risks: special PLLA/PLLTV set_rate depends on previous determine_rate storing parameters in `clk->p`; direct set_rate without a matching determine call can use stale state. PLLTV fractional search is complex and has TODO FVCO range comments. Default gate enabling may conflict with low-power expectations. `sp_pll_calc_div()` can produce zero only if unusual base/rate inputs occur, but hardware divider encoding assumes `fbdiv - 1`. Gate names are generated positional strings, making diagnostics less semantic.

Test signals: boot-time provider registration, all DT clock indices, PLL bypass and non-bypass rate round trips, PLLTV integer/fractional rates, PLLA table rates, default gate masks, and consumer probes for peripherals. No direct tests exist.
