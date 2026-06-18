# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3519.c

Purpose: implements the Hi3519 CRG clock/reset platform driver with fixed-rate roots, one FMC mux, peripheral gates, OF clock provider registration, and reset controller setup.

Important APIs/types/functions: `hi3519_fixed_rate_clks` defines 24 MHz through 400 MHz roots. `hi3519_mux_clks` defines `fmc_mux` with an eight-entry hardware table. `hi3519_gate_clks` gates FMC, UART0-4, and SPI0-2. `hi3519_clk_register()` and `hi3519_clk_unregister()` manage clock provider lifecycle; `hi3519_clk_probe()` integrates reset initialization.

Control flow: probe allocates `hi3519_crg_data`, initializes reset controller, registers fixed rates, muxes, gates, adds an OF onecell provider, and stores drvdata. Remove tears down reset and unregisters clocks/provider.

State and persistence: state is in CRG registers mapped by shared Hisilicon helpers and in allocated clock/reset data. No durable state exists across reboot.

Dependencies and integration points: uses `dt-bindings/clock/hi3519-clock.h`, shared `clk.h` helpers, `reset.h`, OF platform matching on `hisilicon,hi3519-crg`, and `core_initcall()` for early availability.

Risks: unwind labels are ordered oddly: on mux registration failure the `unregister_fixed_rate` label is used correctly, but subsequent labels require care when edited. Probe treats reset init failure as `-ENOMEM` even if the underlying cause differs. Only a small set of peripherals is represented here.

Test signals: boot/probe with Hi3519 DT, verify clock IDs resolve, toggle FMC/UART/SPI gates, exercise reset controller consumers, and unload/remove in module builds.
