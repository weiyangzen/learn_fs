# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.c

## Purpose
This file is the shared implementation for StarFive JH71x0 register-backed clocks. It provides common ops for gates, dividers, fractional dividers, muxes, mux-dividers, gate-mux-dividers, and inverters.

## Important APIs, Types, And Functions
`starfive_jh71x0_clk_ops(max)` selects a `clk_ops` table based on encoded capability bits in the per-clock `max` field. `jh71x0_clk_get()` is the generic OF onecell lookup. Internal helpers include `jh71x0_clk_reg_get()`, `jh71x0_clk_reg_rmw()`, enable/disable/is_enabled, integer and fractional rate operations, parent get/set, phase get/set, and debugfs register export.

## Control Flow
Domain drivers allocate `struct jh71x0_clk_priv` with a flexible `reg[]` array, fill each `jh71x0_clk`, and register it with ops selected by `max`. At runtime, clock framework callbacks read or update `base + 4 * idx`. Read-modify-write operations are serialized by `priv->rmw_lock`.

## State And Persistence
Persistent state is one 32-bit hardware register per clock. The register format uses bit 31 enable, bit 30 invert, bits 27:24 mux, and bits 23:0 divider or fractional divider data. Driver state stores the mapped base, lock, optional PLL fallback pointers, notifier state, and per-clock max divider.

## Dependencies And Integration Points
It depends on Linux common clock APIs, debugfs, MMIO access, and the macros/types in `clk-starfive-jh71x0.h`. It exports symbols for all StarFive JH7100/JH7110 domain drivers.

## Risks
`starfive_jh71x0_clk_ops()` infers behavior from `max`; a wrong macro in a table can select the wrong ops. Divider recalc returns zero for a register divider of zero, so reset-default hardware must be initialized by firmware or set before use. Fractional arithmetic multiplies parent rates by 100 and should be checked for overflow on future higher-rate parents.

## Test Signals
Unit-level signals include ops selection for every macro family, enable/rate/parent/phase callbacks, concurrent RMW safety, debugfs register visibility, and full-domain boot tests for JH7100 and JH7110.
