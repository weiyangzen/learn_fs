# sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.c

Purpose: provides a small legacy clock implementation for Lantiq MIPS platforms and initializes the MIPS high-precision timer frequency.

Important APIs/functions: `clkdev_add_static`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, `clk_get_rate`, `clk_set_rate`, `clk_round_rate`, `clk_enable`, `clk_disable`, `clk_activate`, `clk_deactivate`, and `plat_time_init`. `get_counter_resolution()` reads hardware register `$3` via `rdhwr`.

Control flow: SoC-specific code calls `clkdev_add_static()` to seed CPU/FPI/IO/PPE rates. Generic clock accessors validate `struct clk`, then return stored rates or call callbacks. `plat_time_init()` calls `ltq_soc_init()`, computes `mips_hpt_frequency` from CPU rate and counter resolution, resets compare, and prints CPU clock.

State and persistence: static `cpu_clk_generic[4]` holds clock rates for the booted SoC; no dynamic parent tree or persistence exists.

Dependencies and integration: integrates with Linux `clkdev`, MIPS timer setup, and Lantiq SoC init code in XWAY/Falcon.

Risks: invalid clocks often return `0` or `-1` instead of standard errno. `clk_set_parent()` and `clk_get_parent()` are stubs. Timer frequency depends on correct CPU rate and counter resolution.

Test signals: boot log CPU clock value, timer tick stability, driver clock lookup for FPI/IO/PPE, and build checks with Lantiq SoCs.
