# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.c

## Purpose
Implements Krait CPU/L2 clock mux and divider ops using ARM L2 indirect registers. It supports parent switching for primary/secondary muxes and a divider that is commonly used as divide-by-2 in Krait clock trees.

## Important APIs, Types, And Functions
Exports `krait_mux_clk_ops` and `krait_div2_clk_ops`. Key helpers are `__krait_mux_set_sel()`, `krait_mux_set_parent()`, `krait_mux_get_parent()`, `krait_div2_determine_rate()`, `krait_div2_set_rate()`, and `krait_div2_recalc_rate()`. A global `krait_clock_reg_lock` serializes indirect register access.

## Control Flow
Mux set-parent converts the CCF parent index to a hardware value, caches it in `en_mask`, and only writes hardware if the clock is enabled. The write path optionally disables secondary source clock gating for APQ/IPQ8064 errata, updates primary and low-power fields, restores gating, delays for switch completion, and releases the lock. Divider set-rate clears divider bits under the same lock; determine-rate asks the parent for twice the requested rate and reports half of the rounded parent.

## State And Persistence
State persists in Krait L2 indirect registers and descriptor fields such as `en_mask`, `reparent`, `safe_sel`, and `old_index`. The global lock protects shared primary/secondary mux register updates. No regmap is used; this is CPU coprocessor style register access.

## Dependencies And Integration Points
Depends on `asm/krait-l2-accessors.h`, CCF mux helpers, spinlocks, delays, and descriptor definitions in `clk-krait.h`. Krait CPU clock drivers use these ops for safe parent switching and PLL/divider composition.

## Risks And Edge Cases
Writing mux registers while a CPU clock is off is avoided because it may not work. Parent map errors produce wrong hardware selections. Low-power (`lpl`) mode duplicates fields at an offset, so descriptor shifts/masks must be correct. Errata handling must wrap the switch exactly for affected hardware.

## Test Signals
Parent switch while enabled and disabled, low-power field mirroring, errata gating toggle, divider recalc for raw divider values, and concurrent mux/divider operations are the main signals.
