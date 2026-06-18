<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.c

## Purpose

`icst.c` implements pure rate-conversion math for ICST307 and ICST525 clock generators.

## Important APIs, Types, And Functions

It exports chip-specific `s2div` and `idx2s` lookup tables. `icst_hz()` converts an `icst_vco` tuple to Hz using `ref * 2 * (v + 8) / ((r + 2) * s2div[s])`. `icst_hz_to_vco()` searches output-divider and reference-divider combinations to find the closest representable VCO for a requested frequency within parameter limits.

## Control Flow

Rate search first chooses an output divider whose PLL frequency is inside the allowed range, then scans `rd_min..rd_max`, computes the nearest V divider, and records the smallest absolute frequency difference.

## State And Persistence Behavior

There is no mutable state. All behavior is deterministic from `icst_params` and requested rate.

## Dependencies And Integration Points

It depends on 64-bit division helpers and `icst.h`. `clk-icst.c` uses these functions for CCF recalc, determine, and set-rate paths; symbols are exported for other in-kernel ICST users.

## Risks And Test Signals

Risks include integer rounding edge cases, returning a default max tuple when no divider fits, and parameter tables that use actual divider values versus encoded register values. Unit-style tests should cover min/max boundaries, exact frequencies, and known ICST307/525 board rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.c -->
