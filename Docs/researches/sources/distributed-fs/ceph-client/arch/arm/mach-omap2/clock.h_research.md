<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.h

## Purpose
Defines OMAP2+ clock shared constants, rate-table flags, DPLL mode encodings, and declarations for low-level clock setup and feature initialization.

## Important APIs, Types, and Functions
Provides `RATE_IN_*` flags, `CORE_CLK_SRC_*` values, OMAP2/3/4 DPLL mode encodings, extern `omap_clk_ll_ops`, `omap2_clk_setup_ll_ops()`, and `ti_clk_init_features()`.

## Control Flow
No runtime flow in the header. Its constants guide clock data tables and feature setup in `clock.c` and OMAP2xxx clock files.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on Linux clk provider/devres and TI clock framework headers. Used by OMAP2+ clock, PRCM, and OPP data code.

## Risks
Mode encodings must match hardware CM register fields. Rate flags determine which table entries are valid for SoC revisions; mistakes can expose unsupported clock rates.

## Test Signals
Compile all OMAP2+ clock tables and run clock rate enumeration on each SoC revision. Static checks should compare DPLL mode constants with TRM values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.h -->
