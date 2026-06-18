# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc2xxx.c

## Purpose
Implements OMAP2xxx SDRAM timing and DLL handling used during CORE DPLL rate changes.

## APIs, Flow, And State
State includes static `struct memory_timings mem_timings` and `curr_perf_level`. `omap2xxx_sdrc_dll_is_unlocked()` checks the DLLA control unlock bit. `omap2xxx_sdrc_reprogram(level, force)` selects slow or fast DLL control for `CORE_CLK_SRC_DPLL` vs `CORE_CLK_SRC_DPLL_X2`, writes PRCM voltage setup, calls `omap2_sram_reprogram_sdrc()` with interrupts disabled, and updates current performance level. `omap2xxx_sdrc_init_params(force_lock_to_unlock_mode)` detects SDR vs DDR, chooses base chip select, reads current DLL control/status, derives fast and slow DLL values, and calls SRAM initialization to calibrate slow DLL control.

## Dependencies And Integration
Depends on SoC detection, PRM2xxx voltage setup registers, SDRC accessors, clock constants, and SRAM helper routines. Used by the clock framework during OMAP2 CORE DPLL changes.

## Risks And Test Signals
The code disables interrupts and changes memory controller timing from SRAM; mistakes can crash the system immediately. It writes raw PRCM voltage setup addresses with a TODO to abstract through PRM. Test signals are successful CORE DPLL transitions, correct DLL lock/unlock status, and memory stability after frequency changes.
