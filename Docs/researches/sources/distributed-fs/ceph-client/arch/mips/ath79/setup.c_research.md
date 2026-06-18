## sources/distributed-fs/ceph-client/arch/mips/ath79/setup.c

Purpose: implements core ATH79 platform setup: SoC identification, FDT setup, reset/PLL mapping, DDR controller init, memory detection, halt/poweroff hooks, timer frequency initialization, and irqchip initialization.

Important APIs and functions: `plat_mem_setup()` is the early setup entry. `ath79_detect_sys_type()` decodes `AR71XX_RESET_REG_REV_ID`, sets `ath79_soc`/`ath79_soc_rev`, formats `ath79_sys_type`, and prints it. `get_system_type()` returns the formatted string. `plat_time_init()` initializes OF clocks, obtains CPU node clock 0, logs CPU MHz, and sets `mips_hpt_frequency`. `arch_init_irq()` calls `irqchip_init()`. `get_c0_compare_int()` returns the legacy CP0 compare IRQ.

Control flow: memory setup sets I/O port base, locates the FDT from firmware `fdt_start` or built-in `get_fdt()`, calls `__dt_setup_arch()`, maps reset and PLL bases, detects SoC, initializes DDR controller bases, scans memory between 2 and 256 MiB, and installs halt/poweroff. Time init runs OF clock declarations, fetches the CPU clock, and derives the high-precision timer from CPU/2.

State and persistence: global `ath79_reset_base`, `ath79_pll_base`, `ath79_soc`, `ath79_soc_rev`, and static `ath79_sys_type` are set for this boot. No durable storage is written.

Dependencies and integration: depends on firmware helpers, OF/FDT, common clock framework, irqchip DT, MIPS time/reboot, ATH79 register macros, and DDR helpers from `common.c`.

Risks: unknown revision IDs panic. Missing CPU node or clock leaves timer setup incomplete after logging an error. Memory detection uses broad bounds and assumes low memory starts at 0. `ath79_halt()` loops in `cpu_wait()` forever.

Test signals: boot log should show exact SoC string and CPU clock. `/proc/cpuinfo` system type should match. IRQ controllers should initialize from DT, timers should tick at the correct rate, and detected RAM should match hardware.
