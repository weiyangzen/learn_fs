# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apbc.c

Purpose: This file implements APB clock gate/reset preparation for Marvell MMP peripheral clocks controlled by APBC registers.

Important APIs, types, and functions: The public constructor is `mmp_clk_register_apbc`. Internal state is `struct clk_apbc` with `clk_hw`, MMIO base, delay, APBC flags, and optional spinlock. The ops table `clk_apbc_ops` provides `prepare` and `unprepare` through `clk_apbc_prepare` and `clk_apbc_unprepare`.

Control flow: Registration allocates a `clk_apbc`, fills `clk_init_data` with `CLK_SET_RATE_PARENT`, records register metadata, and calls `clk_register`. Prepare optionally locks, sets power and functional clock bits, waits the configured delay, sets APB bus clock, waits again, then deasserts reset unless `APBC_NO_BUS_CTRL` is set. Unprepare clears optional power and functional clock bits, delays, then clears APB bus clock.

State and persistence behavior: There is no managed lifetime beyond freeing on registration failure; successful clocks are unmanaged legacy CCF registrations. Runtime state is the APBC hardware register. Optional spinlock protects registers shared with mux clocks or other bitfields.

Dependencies and integration points: It depends on `clk.h` for APBC flag definitions and declarations, MMIO accessors, delays, CCF, and slab allocation. MMP SoC clock provider files call this helper for APB peripherals.

Risks and edge cases: Reset, functional clock, bus clock, and power sequencing must match hardware requirements. Shared registers require callers to pass the right lock. Delay values must be sufficient for hardware stabilization. Test signals include prepare/unprepare register traces, APBC_POWER_CTRL and APBC_NO_BUS_CTRL variants, shared-register lock coverage, and peripheral probe/remove using APBC clocks.
