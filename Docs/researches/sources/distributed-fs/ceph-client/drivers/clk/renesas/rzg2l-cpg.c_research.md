# sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.c

## Purpose
Implements the common CPG backend for Renesas RZ/G2L-family and related RZ/G3S SoCs. It registers core PLL, divider, mux, SD-mux, DSI/PLL5, and module clocks; handles module MSTOP control; exposes resets; and creates an always-on PM domain that attaches eligible module clocks to device PM.

## Important APIs, Types, and Functions
`struct rzg2l_cpg_priv` stores MMIO base, lock, clocks, reset controller, SoC info, PM domain, and cached PLL5/DSI divider choices. `rzg2l_cpg_register_core_clk()` dispatches all core clock descriptor types. `rzg2l_cpg_sd_clk_mux_notifier()` switches SD muxes through a safe 266 MHz intermediate. `rzg3s_cpg_div_clk_notifier()` avoids invalid divider/parent combinations. Module clocks use `struct mod_clock` plus shared `struct mstop` counters.

## Control Flow, State, and Persistence
Probe maps registers, allocates clocks, registers core/module clocks, initializes MSTOP state, installs the OF provider, adds the PM domain, registers resets, deasserts critical resets, and creates debugfs `mstop`. Dynamic divider and mux writes use hiword fields under `rmw_lock` and poll status. SIPLL5/DSI rate changes compute PLL parameters, program standby/clock registers, wait for lock, and program DSI divider fields. Coupled clocks use soft enabled state around one hardware bit.

## Dependencies, Integration Points, Risks, and Test Signals
The driver integrates with CCF, OF providers, reset-controller, generic PM domains, `pm_clk`, debugfs, and SoC descriptors. It exports `rzg2l_cpg_dsi_div_set_divider()`. Risks include static DSI divider globals, PLL5 search failures, shared MSTOP count bugs, and monitor timeouts. Test SDHI/G3S rate changes, DSI pixel clocks, debugfs MSTOP state, coupled clocks, resets, and resume of critical clocks.
