# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.h

## Purpose
Declares the descriptor contract for Qualcomm HFPLL clocks. The header separates immutable register metadata from the runtime clock wrapper used by `clk-hfpll.c`.

## Important APIs, Types, And Functions
`struct hfpll_data` lists mode, L/M/N, user, droop, config, status registers, lock bit, initial values, VCO mask, low-VCO maximum rate, and min/max rates. `struct clk_hfpll` stores a descriptor pointer, init flag, embedded `clk_regmap`, and spinlock. It exports `clk_ops_hfpll` and `to_clk_hfpll()`.

## Control Flow
SoC code fills an `hfpll_data` instance, embeds a `clk_hfpll`, and registers it with `clk_ops_hfpll`. Runtime behavior is implemented by the C file, which reads descriptor fields to initialize, enable, disable, recalc, and set rates.

## State And Persistence
The header defines both static descriptor state and runtime `init_done`/lock state. Hardware persistence is represented by the register addresses and initial values in `hfpll_data`.

## Dependencies And Integration Points
Includes CCF provider APIs, spinlocks, and `clk-regmap.h`. It integrates with regmap-backed Qualcomm clock controllers needing legacy HFPLL support.

## Risks And Edge Cases
All semantics depend on accurate register addresses and initial values. Missing optional fields are represented as zero, so zero can only be used for optional registers when that is not a valid target on the platform.

## Test Signals
Build coverage for descriptors, correct container conversion, and runtime tests through `clk_ops_hfpll` validate the header.
