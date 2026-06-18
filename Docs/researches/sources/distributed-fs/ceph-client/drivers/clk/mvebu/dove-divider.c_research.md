# sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.c

Purpose: Dove PMU core PLL divider provider for AXI, GPU, VMeta, and LCD clocks.

Important APIs/functions: `dove_divider_clk_init` maps registers, calls `dove_divider_init`, and publishes a onecell provider. Custom divider ops are `dove_recalc_rate`, `dove_determine_rate`, and `dove_set_clock`.

Control flow: init registers a fixed 2 GHz `core-pll`, then registers four custom divider clocks. Set-rate computes a divider or table encoding, builds mask/load bits, and calls `dove_load_divider`, which deasserts reset, writes divider value, pulses load, delays 250 ns, and clears load.

State and persistence: divider settings live in PMU `DIV_CTRL0/1`; static `dove_hw_clocks` carries per-clock bit fields and lock pointer.

Dependencies and integration: called from `dove.c`, CCF, MMIO, spinlock, and Dove DT divider node.

Risks: `axi_divider` starts with `(u32)-1` as a sentinel-like table entry, which can surprise rate calculations. Fixed 2 GHz core PLL is an assumption due to sparse documentation. No unregister path for early init.

Test signals: Dove boot `clk_summary`, AXI/GPU/VMeta/LCD rate changes, register load pulse timing, and divider table edge cases.
