<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpll.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpll.c

## Purpose
Defines OMAP2xxx DPLL clock hardware operations for allowing or denying automatic DPLL idle.

## Important APIs, Types, and Functions
Provides `const struct clk_hw_omap_ops clkhwops_omap2xxx_dpll` with `.allow_idle` and `.deny_idle` callbacks.

## Control Flow
`_allow_idle()` validates the clock and DPLL data pointer, then programs CM to allow DPLL automatic low-power stop. `_deny_idle()` similarly disables DPLL autoidle.

## State and Persistence Behavior
No private state. Hardware state is the CM DPLL autoidle setting.

## Dependencies and Integration Points
Depends on OMAP2xxx CM helper functions and TI OMAP clock hardware structures.

## Risks
Callbacks silently do nothing for missing DPLL data, which avoids crashes but can hide clock registration problems. Wrong autoidle state can affect latency or power.

## Test Signals
Clock framework tests should call allow/deny idle on OMAP2xxx DPLLs and verify CM autoidle bits. Invalid/null DPLL-data paths should be harmless.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpll.c -->
