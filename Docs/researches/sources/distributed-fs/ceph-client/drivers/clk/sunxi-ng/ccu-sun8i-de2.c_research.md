# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.c

## Purpose

This file implements the CCU for Allwinner display-engine 2/3/3.3 clock blocks. It provides mixer, writeback, and rotation bus/module gates plus intermediate dividers, with descriptor variants for A83T, H3, R40, V3s, A64, H5, H6, and H616 DE33.

## Important APIs, types, and functions

Important objects are shared clock definitions `bus_mixer*`, `bus_wb`, `bus_rot`, `mixer*`, `wb`, `rot`, divider variants parented by either `de` or `pll-de`, variant-specific `clk_hw_onecell_data`, reset maps, and `sunxi_ccu_desc` instances. The entry point is `sunxi_de2_clk_probe()`, matched by `sunxi_de2_clk_ids`.

## Control flow, state, and persistence

Probe obtains variant match data, maps registers, gets parent `bus` and `mod` clocks, gets an exclusive reset, enables bus and module clocks, deasserts reset, optionally writes two DE33-specific unknown initialization registers for H616, then registers the CCU. Error paths assert reset and disable prepared clocks. Successful probe deliberately leaves bus/mod clocks enabled so the DE CCU registers remain accessible.

## Dependencies and integration points

The driver depends on `clk`, `reset`, OF matching, and sunxi-ng CCU helpers. It integrates with the main CCU as a consumer of the parent bus/mod clocks and as a provider to DRM/display-engine users for mixers, writeback, and rotation.

## Risks and test signals

Risks include variant matrix mistakes, shared reset-line comments for mixer1/writeback, wrong parent choice between `de` and `pll-de`, and the opaque DE33 initialization writes. Test with DRM display bring-up on each compatible, writeback/rotation where present, reset handling on probe failure, and `clk_summary` showing expected exposed IDs for one-mixer versus two-mixer variants.
