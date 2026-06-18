<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock2xxx.h

## Purpose
Small OMAP2xxx clock header that exposes the CORE clock rate query for OMAP2xxx-specific clock and DVFS code.

## Important APIs, Types, and Functions
Declares `omap2xxx_clk_get_core_rate()` and includes shared `clock.h`.

## Control Flow
No runtime flow. Implemented in `clkt2xxx_dpllcore.c` and consumed by virtual PRCM set/rate code.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on the OMAP2+ clock headers and Linux clock provider definitions.

## Risks
The single exported helper relies on `omap2xxx_clkt_dpllcore_init()` having stored the DPLL/core clock pointer before use.

## Test Signals
Build OMAP2xxx clock code and verify callers can query a nonzero core rate after clock init.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock2xxx.h -->
