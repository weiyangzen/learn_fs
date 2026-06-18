# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.h

## Purpose
Declares OMAP2/3 SDRC/SMS MMIO accessors, SDRC timing data structures, initialization/reprogramming APIs, register offsets, power-control fields, and reference refresh constants.

## APIs, Flow, And State
Outside assembly, the header exports global base pointers, address macros, inline `sdrc_read/write_reg()` and `sms_read/write_reg()`, `omap2_set_globals_sdrc()`, `struct omap_sdrc_params`, `omap2_sdrc_init()`, `omap2_sms_restore_context()`, `struct memory_timings`, and OMAP2xxx SDRC DLL/reprogramming APIs. In assembly, it provides physical address macros. Register offsets cover SDRC sysconfig, chip select config, DLL A/B control/status, power, mode/config/timing/refresh/manual registers for CS0/CS1, and SMS sysconfig. Constants describe DLL lock minimum frequency, fixed-point scaling, stabilization loops, and refresh values.

## Dependencies And Integration
Included by `sdrc.c`, `sdrc2xxx.c`, and OMAP2/3 sleep assembly. It bridges C SDRC initialization with SRAM/assembly suspend code that must access registers while caches/MMU may be constrained.

## Risks And Test Signals
The timing constants are hardware- and board-sensitive, and comments note that optimal refresh values are not universal. Test signals are SDRC DLL lock status, DPLL rate changes, memory stability at low/high frequencies, and off-mode resume.
