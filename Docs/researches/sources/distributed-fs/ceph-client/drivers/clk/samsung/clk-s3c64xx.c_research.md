# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s3c64xx.c

Purpose: S3C6400/S3C6410 Samsung clock tree description and initializer.

Important APIs/types/functions: `s3c64xx_clk_init()`; DT entry points `s3c6400_clk_init()` and `s3c6410_clk_init()`; fixed-rate, mux, divider, gate, PLL, register-save, and clkdev alias arrays; gate helper macros for bus/source/always-on gates.

Control flow: maps CMU registers, allocates a Samsung provider, optionally registers legacy external fixed clocks, registers PLLs and common clocks, selects S3C6400 or S3C6410-specific mux/div/gate/alias tables, registers PM save lists, publishes the OF provider, and logs derived rates.

State and persistence behavior: static `reg_base` and `is_s3c6400`; hardware CMU register state; suspend/resume state via `s3c64xx_clk_regs` and S3C6410 extra registers through Samsung common sleep support.

Dependencies/integration points: `dt-bindings/clock/samsung,s3c64xx-clock.h`, Samsung `clk.h`/`clk-pll.h`, CCF, OF address mapping, and legacy device names for clkdev lookup.

Risks: literal register/bit tables and DT IDs are fragile; parent-name differences between S3C6400 and S3C6410 matter; legacy aliases are ABI. The local source contains a duplicated `SCLK_LCD27` gate entry.

Test signals: boot S3C6400/S3C6410 DTs, inspect `clk_summary`, validate UART/MMC/I2S/USB aliases, confirm logged APLL/MPLL/EPLL/ARM rates, and test suspend/resume.
