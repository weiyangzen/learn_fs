# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.c

## Purpose
Implements Qualcomm branch clock gates that enable, disable, and verify clock branches through regmap-controlled enable and halt/status registers. It provides CCF ops for older branch status formats, CBCR v2 status fields, always-on branches, simple regmap gates, prepare/unprepare gates, and branches associated with memory power gating.

## Important APIs, Types, And Functions
Exports `clk_branch_ops`, `clk_branch2_ops`, `clk_branch2_aon_ops`, `clk_branch_simple_ops`, `clk_branch2_prepare_ops`, and `clk_branch2_mem_ops`. Internal helpers include `clk_branch_in_hwcg_mode()`, `clk_branch_check_halt()`, `clk_branch2_check_halt()`, `clk_branch_wait()`, `clk_branch_toggle()`, and memory-aware enable/disable callbacks.

## Control Flow
Enable paths first set the regmap enable bit through `clk_enable_regmap()`, then wait for the halt/status bit unless the descriptor requests skip, fixed delay, voted-disable behavior, or hardware clock gating mode. Disable clears the enable bit and performs the corresponding status wait. Branch2 status checks examine `CBCR_CLK_OFF` and `CBCR_NOC_FSM_STATUS`. Memory branches assert a memory enable field, poll an ack register, then enable the branch; disable reverses the memory field and disables the branch.

## State And Persistence
Software state is static descriptor data. Persistent hardware state resides in enable bits, halt bits, CBCR status fields, optional hardware-gating registers, and optional memory enable/ack registers. No software cache is maintained, so CCF queries read hardware through regmap.

## Dependencies And Integration Points
Depends on `clk-regmap` helpers, Linux CCF, regmap, bitfield macros, and the descriptor definitions in `clk-branch.h`. SoC clock controller tables embed `struct clk_branch` or `struct clk_mem_branch` and select the exported ops.

## Risks And Edge Cases
Wrong halt polarity or halt_check type can cause false success, spurious timeout, or boot stalls. Hardware-gated mode skips halt polling, so misconfigured H/W CG fields can hide failures. Memory branches can fail before the actual branch is enabled if the ack bit does not assert. Voted clocks delay on disable because status may not reflect a single client.

## Test Signals
Useful tests cover branch enable/disable with both halt polarities, CBCR v2 FSM status, skip and delay modes, hardware clock gating skip, voted clocks, memory ack timeout injection, and prepare/unprepare users.
