# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210-emc.c

## Purpose
This file implements the Tegra210 EMC clock as a common-clock-framework clock. The EMC clock is unusual because memory-controller timing changes are owned by an external EMC provider, not just by the CAR clock driver. This file exposes a clock named `emc`, validates provider timing tables, chooses supported EMC rates, coordinates parent rate changes, and calls the provider's `set_rate()` hook to perform the actual memory timing transition.

## Important APIs, Types, And Functions
The central type is `struct tegra210_clk_emc`, containing `clk_hw`, CAR register base, provider pointer, and parent clock slots. The public entry points are `tegra210_clk_register_emc()`, `tegra210_clk_emc_attach()`, and exported `tegra210_clk_emc_detach()`. Clock operations are `tegra210_clk_emc_get_parent()`, `tegra210_clk_emc_recalc_rate()`, `tegra210_clk_emc_determine_rate()`, and `tegra210_clk_emc_set_rate()`.

The file uses `struct tegra210_clk_emc_provider` and `struct tegra210_clk_emc_config` from shared Tegra clock headers. The parent list is fixed to `pll_m`, `pll_c`, `pll_p`, `clk_m`, `pll_m_ud`, `pll_mb_ud`, `pll_mb`, and `pll_p_ud`.

## Control Flow
Registration allocates `struct tegra210_clk_emc`, initializes a CCF clock named `emc` with `CLK_IS_CRITICAL | CLK_GET_RATE_NOCACHE`, and registers it with eight parents. Attachment takes a provider module reference, iterates every provider config, validates divider parity and MC/EMC ratio flags, decodes source parent index and divisor, and computes or verifies `config->parent_rate`. If validation fails, it drops the module reference and rejects the provider.

Rate requests first round to the nearest provider config at or above the requested rate, falling back to the maximum available config. `set_rate()` selects the same config, compares the current parent rate and configured source, switches to an alternate PLLM/PLLMB parent when the parent rate must change but the encoded parent would otherwise stay the same, sets the chosen parent clock rate, enables the new parent if reparenting, mutates `config->value` with the actual parent index, calls `provider->set_rate(dev, config)`, then reparents the CCF clock and disables the old parent.

## State And Persistence Behavior
The only persistent software state is the provider pointer and module reference. Hardware state lives in `CLK_SOURCE_EMC`; `get_parent()` decodes bits 31:29 and `recalc_rate()` decodes the 2x divisor in bits 7:0. `recalc_rate()` deliberately ignores the cached parent rate argument and reads the actual current parent because EMC transitions can change both parent and parent rate during `set_rate()`.

## Dependencies And Integration Points
This file integrates the CAR clock tree with the Tegra210 EMC/memory timing driver through the provider interface. It uses Linux CCF APIs for parent lookup, rate setting, parent enable/disable, and manual reparenting. It depends on bitfield helpers for decoding register fields and on Tegra210 CAR register definitions shared with `clk-tegra210.c`, which provides low-level EMC register update functions exported for the EMC provider.

## Risks
`tegra210_clk_emc_set_rate()` mutates the provider config's `value` in place when switching parent index, so provider config storage must be writable and callers must tolerate that updated state. `tegra210_clk_emc_find_parent()` converts from `clk_hw` to name and then uses `__clk_lookup()`, which is global-name dependent. Error handling after a successful provider rate switch but failed old-parent lookup returns an error after hardware has already changed. The rate-selection policy rounds upward and only falls back to max; users expecting exact-only matching need to check returned rates.

## Test Signals
Validation signals include provider attach failure for odd divisors or inconsistent MC/EMC ratio flags, correct `clk_round_rate()` behavior against the timing table, successful EMC frequency transitions across PLLM/PLLMB alternate parents, no parent clock leaks after failed transitions, correct `clk_get_rate(emc)` after parent changes, and suspend/resume or memory stress tests while changing EMC rates.
