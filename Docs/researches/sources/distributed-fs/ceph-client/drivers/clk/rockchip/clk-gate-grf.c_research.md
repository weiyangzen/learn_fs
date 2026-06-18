# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-gate-grf.c

## Purpose
Implements Rockchip gate clocks controlled through GRF regmap bits instead of the main CRU gate registers. It supports normal and inverted gate polarity plus optional hiword-mask writes.

## Important APIs, Types, and Functions
`struct rockchip_gate_grf` holds CCF hardware, GRF regmap, register, shift, and gate flags. Enable and disable compute data plus hiword mask and use `regmap_update_bits()`. `rockchip_gate_grf_is_enabled()` uses `regmap_test_bits()` and applies `CLK_GATE_SET_TO_DISABLE`. `rockchip_clk_register_gate_grf()` validates the regmap and registers the clock.

## Control Flow, State, and Persistence
Persistent state is the allocated gate object. Hardware state is the GRF register bit. Enable/disable are direct regmap updates without polling.

## Dependencies, Integration Points, Risks, and Test Signals
The helper depends on CCF, regmap, and SoC descriptions for GRF gate bits. Risks include invalid regmap, wrong polarity flags, and ignored disable errors. Test enable/disable/is_enabled cycles, hiword-mask behavior, and probe behavior without a GRF regmap.
