<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-vexpress-osc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-vexpress-osc.c

## Purpose

`clk-vexpress-osc.c` is a platform driver for Versatile Express configurable OSC clock generators behind the VExpress configuration regmap interface.

## Important APIs, Types, And Functions

`struct vexpress_osc` stores regmap, CCF hardware, and optional min/max rate bounds. CCF ops read the current rate from register 0, clamp requested rates to `freq-range`, and write new rates to register 0. `vexpress_osc_probe()` initializes the config regmap, reads `freq-range` and `clock-output-names`, registers the clock, adds an OF provider, and sets the rate range.

## Control Flow

The module platform driver matches `arm,vexpress-osc`. Probe is device-managed and publishes a simple provider if registration succeeds.

## State And Persistence Behavior

Rate state persists in the VExpress configuration backend. Driver state is devm-managed and contains only bounds and hardware handle.

## Dependencies And Integration Points

It depends on `devm_regmap_init_vexpress_config()`, CCF, platform probing, and VExpress DT bindings.

## Risks And Test Signals

Risks include ignoring `regmap_read()` failures in recalc, invalid `freq-range` ordering, and external firmware constraints not represented by min/max. Test module/built-in probe, rate reads/writes through CCF, and clamping below/above DT limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-vexpress-osc.c -->
