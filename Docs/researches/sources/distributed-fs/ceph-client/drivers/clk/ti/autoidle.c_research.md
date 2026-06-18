# sources/distributed-fs/ceph-client/drivers/clk/ti/autoidle.c

## Purpose

`autoidle.c` provides TI OMAP clock autoidle support. It lets individual OMAP clocks deny or allow hardware autoidle through per-clock callbacks and also tracks generic device-tree autoidle bit definitions for global enable/disable operations.

## Important APIs, Types, And Functions

`struct clk_ti_autoidle` stores a register, bit shift, flags, name, and list node for generic autoidle bits. `autoidle_clks` stores all DT-discovered entries and `autoidle_spinlock` serializes non-atomic read/modify/write operations. `omap2_clk_deny_idle()` and `omap2_clk_allow_idle()` validate a `struct clk`, convert it to `clk_hw_omap`, and call internal helpers that update `autoidle_count` and invoke `deny_idle` or `allow_idle` only on 0-to-1 and 1-to-0 transitions.

`of_ti_clk_autoidle_setup()` parses `ti,autoidle-shift`, register address 0, and optional `ti,invert-autoidle-bit`, then adds the entry to the generic list. `omap2_clk_enable_autoidle_all()` and `omap2_clk_disable_autoidle_all()` walk both CCF OMAP clocks and generic list entries to allow or deny hardware autoidle globally.

## Control Flow

During clock DT setup, nodes with `ti,autoidle-shift` are registered in `autoidle_clks`. During SoC clock init, several TI files call `omap2_clk_disable_autoidle_all()` to force clocks out of autoidle for predictable initialization. Later code can call the enable-all path to restore hardware autoidle. Individual clock users can deny and allow idle around critical sections using the exported functions.

## State And Persistence Behavior

The file maintains two forms of state: per-clock `autoidle_count` in `clk_hw_omap` and a global list of generic autoidle register bits. Hardware autoidle state persists in PRCM registers. The list entries allocated during init are not freed, which matches early boot clock setup lifetime.

## Dependencies And Integration Points

The code depends on TI clock low-level read/write ops, `clock.h`, OMAP CCF iteration via `omap2_clk_for_each()`, and DT properties. It integrates with OMAP APLL, interface clock, DPLL, and clockdomain helpers through `allow_idle`/`deny_idle` callbacks.

## Risks And Edge Cases

`_omap2_clk_allow_idle()` decrements `autoidle_count` without an explicit underflow guard; unbalanced allow calls can wrap the counter and prevent autoidle from being restored. Generic autoidle read/modify/write operations are not locked by `autoidle_spinlock` in the global allow/deny functions, so callers rely on init-time or externally serialized use. Inverted autoidle bits must be described accurately or global enable/disable will do the opposite of what hardware expects.

## Test Signals

Boot logs should show no autoidle setup failures for valid DT nodes. Instrument PRCM registers before and after `omap2_clk_disable_autoidle_all()` and `omap2_clk_enable_autoidle_all()`. Add tests for balanced and intentionally unbalanced deny/allow sequences, and verify inverted-bit DT nodes change in the expected direction.
