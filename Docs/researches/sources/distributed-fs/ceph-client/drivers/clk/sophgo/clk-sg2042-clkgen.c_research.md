# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-clkgen.c

## Purpose
This file is the SG2042 clock-generator driver. It registers divider, gate, and mux clocks fed by SG2042 PLL outputs, arranges them in hardware clock-tree order, and exposes them through a CCF onecell provider for `sophgo,sg2042-clkgen`.

## Important APIs, Types, And Functions
Local clock classes are `struct sg2042_divider_clock`, `struct sg2042_gate_clock`, and `struct sg2042_mux_clock`. Divider ops are implemented by `sg2042_clk_divider_recalc_rate()`, `sg2042_clk_divider_determine_rate()`, and `sg2042_clk_divider_set_rate()`. Mux rate-change safety is implemented by `sg2042_mux_notifier_cb()`.

Registration helpers are `sg2042_clk_register_divs()`, `sg2042_clk_register_gates()`, `sg2042_clk_register_gates_fw()`, `sg2042_clk_register_muxs()`, and `sg2042_init_clkdata()`. Static tables define level-1 gates, level-1 dividers, top-level muxes, level-2 dividers, and level-2 gates.

## Control Flow
Probe maps MMIO resource 0 and calculates the total number of clocks from all tables. It registers level-1 gates first because dividers depend on their returned `clk_hw` pointers. It then registers level-1 dividers, muxes, level-2 dividers, and level-2 gates. During registration, selected returned `clk_hw` pointers are written into one-element parent arrays used by downstream definitions.

Divider set-rate asserts reset, writes divider factor and factor-source bit, then deasserts reset under a shared lock. Read-only dividers return the current/default divider during determine-rate. Non-read-only muxes register a notifier that switches the mux to FPLL before a parent rate change and restores the original parent afterward.

## State And Persistence
`struct sg2042_clk_data` stores MMIO base and onecell output. Static parent arrays start as NULL and are patched during registration to connect generated `clk_hw`s. Divider hardware state is in `CLKDIVREG*` registers, including reset, factor-select, and factor fields. Gate state is in `CLKENREG*`; mux state is in `CLKSELREG0`.

## Dependencies And Integration Points
The driver depends on SG2042 PLL clocks named by firmware (`mpll`, `fpll`, `dpll0`, `dpll1`) and dt-binding IDs from `sophgo,sg2042-clkgen.h`. It uses generic CCF gate, mux, and divider helpers plus the shared `sg2042_clk_data` type from `clk-sg2042.h`.

## Risks
The parent arrays patched during registration make ordering essential; reordering tables or registration calls can leave downstream parents NULL. The notifier uses magic parent indices where index 1 is FPLL, noted by a FIXME. Some clocks are intentionally inaccurate because fixed 1/2 dividers are not modeled for PCIe AXI clocks. Divider default `initval` values compensate for unreadable hardware defaults; wrong defaults yield wrong reported rates.

## Test Signals
Boot SG2042 with PLL and CLKGEN nodes and verify all binding IDs resolve. Test rate changes for RP CPU normal and AXI DDR mux paths to ensure notifier switching is correct. Inspect `clk_summary` for DDR, timer, UART, eMMC, SD, GPIO debounce, Ethernet, and AXI rates. Confirm read-only DDR dividers refuse changes but report expected defaults.
