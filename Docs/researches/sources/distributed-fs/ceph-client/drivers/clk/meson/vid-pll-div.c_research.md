# sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.c

Purpose: This file implements a read-only Meson video PLL fractional divider. It decodes hardware `shift_val` and `shift_sel` fields into a small set of known Amlogic fractional divide ratios used by video clocking.

Important APIs, types, and functions: The exported ops table is `meson_vid_pll_div_ro_ops`. Internal data includes `struct vid_pll_div`, the `vid_pll_div_table[]` of supported ratios from `/2` through `/15`, `_get_table_val`, and `meson_vid_pll_div_recalc_rate`.

Control flow: CCF calls `recalc_rate`; the driver reads the `val` and `sel` fields from the `meson_vid_pll_div_data`, looks for a matching entry in `vid_pll_div_table`, and computes `parent_rate * multiplier / divider` rounded up. Unsupported register encodings log a debug message and return zero. Init is the standard `clk_regmap_init`.

State and persistence behavior: There is no writable or cached state. The hardware register fields hold the current divider encoding, but this implementation only reports the resulting rate. The TODO in S4 users notes a future writable ops variant could be added.

Dependencies and integration points: It depends on `clk-regmap`, `parm`, CCF, and `vid-pll-div.h`. S4 peripheral video PLL definitions use it to model the divided HDMI PLL input before the rest of the VCLK tree.

Risks and edge cases: Unknown hardware encodings produce a zero rate, which can propagate into display clock calculations. The table only covers common vendor-provided ratios, so new SoCs or firmware settings may need additional entries. Test signals include reading known display modes from clk summary, forcing firmware-supported divider values, and confirming unsupported values fail visibly without crashing.
