<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-impd1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-impd1.c

## Purpose

`clk-impd1.c` registers the two ICST525 VCO clocks on ARM Integrator/IM-PD1 expansion boards.

## Important APIs, Types, And Functions

It defines two `icst_params` tables for 24 MHz reference ICST525 VCOs and two descriptors at offsets `IMPD1_OSC1` and `IMPD1_OSC2` sharing `IMPD1_LOCK`. `integrator_impd1_clk_spawn()` recognizes child compatibles `arm,impd1-vco1` and `arm,impd1-vco2`, reads output name and parent, and calls `icst_clk_setup()` with `ICST_INTEGRATOR_IM_PD1`.

## Control Flow

The built-in platform driver matches `arm,im-pd1-syscon`. Probe iterates available child nodes and spawns an ICST clock for each recognized VCO child. Successful clocks are registered as simple OF providers.

## State And Persistence Behavior

State is the syscon-backed ICST register state plus CCF registrations. The driver has no remove path because it is built-in platform infrastructure.

## Dependencies And Integration Points

It depends on syscon regmap lookup, ICST helpers, platform-driver probing, and IM-PD1 DT child compatibles.

## Risks And Test Signals

Risks are missing syscon parent regmap, unknown child compatibles aborting probe, and incorrect VCO offsets. Test by probing an IM-PD1 DT, changing both VCO rates, and verifying consumers resolve child clock providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-impd1.c -->
