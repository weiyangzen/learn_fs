<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcmu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcmu.c

## Purpose

`clk-prcmu.c` wraps Ux500 PRCMU firmware clock services as Linux CCF clocks. It supports simple gates, scalable clocks, rate-only clocks, OPP/voltage-coupled gates, and two external `clkout` outputs.

## Important APIs, Types, And Functions

`struct clk_prcmu` stores the PRCMU clock selector and whether an OPP request is active. Core callbacks call `prcmu_request_clock()`, `prcmu_clock_rate()`, `prcmu_round_clock_rate()`, and `prcmu_set_clock_rate()`. OPP variants add/remove `PRCMU_QOS_APE_OPP` requirements or call `prcmu_request_ape_opp_100_voltage()`. Public helpers include `clk_reg_prcmu_scalable()`, `clk_reg_prcmu_gate()`, `clk_reg_prcmu_scalable_rate()`, `clk_reg_prcmu_rate()`, `clk_reg_prcmu_opp_gate()`, `clk_reg_prcmu_opp_volt_scalable()`, and `clk_reg_prcmu_clkout()`.

## Control Flow

`clk_reg_prcmu()` allocates a clock, optionally programs an initial rate, initializes CCF metadata, and registers `clk_hw`. Runtime prepare/unprepare delegates clock enablement to firmware. `clkout` clocks configure hardware in prepare and disable by reprogramming divider zero.

## State And Persistence Behavior

Persistent state lives in PRCMU firmware/hardware. Software only tracks OPP request ownership and `clkout` source/divider. Rate-only clocks can report and set PRCMU rates without prepare callbacks.

## Dependencies And Integration Points

It depends on `linux/mfd/dbx500-prcmu.h`, CCF, and the U8500 clock-definition file. Consumers reach these clocks through the PRCMU onecell provider.

## Risks And Test Signals

Risks include leaked OPP requirements on failed disable, bad initial-rate programming, and invalid `clkout` source/divider combinations. Test PRCMU firmware calls, rate rounding, OPP add/remove balance, external clkout parent changes while prepared, and clock-provider IDs from U8500 DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcmu.c -->
