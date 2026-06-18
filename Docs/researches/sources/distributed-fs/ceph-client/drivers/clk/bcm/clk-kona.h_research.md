# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.h

## Purpose
Defines the Broadcom Kona CCU descriptor model used by setup and runtime code. It captures policy masks, gate variants, hysteresis bits, fixed and variable dividers, parent selectors, triggers, peripheral clock data, CCU data, and macros for static SoC clock tables.

## Important APIs, Types, And Functions
Core types are `bcm_clk_policy`, `bcm_clk_gate`, `bcm_clk_hyst`, `bcm_clk_div`, `bcm_clk_sel`, `bcm_clk_trig`, `peri_clk_data`, `kona_clk`, `bcm_lvm_en`, `bcm_policy_ctl`, `ccu_policy`, and `ccu_data`. Macros such as `POLICY`, `HW_SW_GATE`, `HW_SW_GATE_AUTO`, `HW_ENABLE_GATE`, `SW_ONLY_GATE`, `HW_ONLY_GATE`, `HYST`, `FIXED_DIVIDER`, `DIVIDER`, `FRAC_DIVIDER`, `SELECTOR`, `TRIGGER`, `CLOCKS`, `KONA_CLK`, and `KONA_CCU_COMMON` build static descriptors.

## Control Flow
The header itself is declarative. Setup code validates these descriptors and registers clocks; runtime code uses the same fields to decide which registers to read/write, how to map common-clock parent indexes to hardware selector values, and how to compute scaled divider rates.

## State And Persistence
Some descriptor fields are mutable runtime state, notably gate flags for software-managed enabled state, `bcm_clk_div.u.s.scaled_div`, `bcm_clk_sel.parent_sel`, `bcm_clk_sel.parent_count`, and `bcm_clk_sel.clk_index`. `ccu_data` persists the mapped base, lock, write-enable state, node, range, and flexible `kona_clks` array.

## Dependencies And Integration Points
Includes common clock and OF headers and exports `kona_peri_clk_ops`, `scaled_div_max`, `kona_dt_ccu_setup`, and `kona_ccu_init` for SoC files and setup/runtime split compilation.

## Risks And Edge Cases
Descriptors use flag macros and sentinel values such as `BAD_CLK_INDEX`, `BAD_CLK_NAME`, and `BAD_SCALED_DIV_VALUE`; misuse can silently change setup behavior. Because `kona_clk` embeds `clk_init_data`, parent arrays allocated during setup must remain valid until teardown.

## Test Signals
Static table validation, sparse parent selector mappings, fractional divider scale bounds, gate variants, CCU policy descriptors, and compile coverage of all macros are the key signals.
