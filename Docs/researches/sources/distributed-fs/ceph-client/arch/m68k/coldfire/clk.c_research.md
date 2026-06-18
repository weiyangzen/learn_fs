# sources/distributed-fs/ceph-client/arch/m68k/coldfire/clk.c

Purpose: simple ColdFire clock framework glue for legacy platform clocks.

Important APIs are `clk_enable()`, `clk_disable()`, `clk_get_rate()`, dummy `clk_round_rate()`, `clk_set_rate()`, `clk_set_parent()`, `clk_get_parent()`, and optional power-management helpers `__clk_init_enabled()`/`__clk_init_disabled()` plus `clk_ops0`/`clk_ops1`. Clock enable/disable uses a spinlock and reference count in `struct clk`.

Control flow: `clk_enable()` returns success for NULL, otherwise increments `clk->enabled` and invokes `clk_ops->enable()` only on transition from 0 to 1. `clk_disable()` decrements and invokes disable only on transition to 0. On SoCs with `MCFPM_PPMCR0/1`, ops write the clock slot to power-management control/status registers.

State is per-clock `enabled` count, `rate`, optional `slot`, and power-management hardware registers. The global `clk_lock` serializes reference-count transitions.

Dependencies include `asm/mcfclk.h` clock structures, ColdFire power-management register macros, raw I/O writes, and Linux clk consumers. Integration is used by ColdFire SOC files that define clock lookup tables and operations.

Risks and test signals: underflow in `clk_disable()` is not guarded; dummy rate/parent setters warn if called with a clock, so consumers must not expect full common-clock semantics. Test balanced enable/disable pairs, peripheral probing that depends on clocks, and SoC variants with and without `MCFPM_PPMCR1`.
