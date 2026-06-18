<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock_data.c

Purpose: Declarative OMAP1 clock tree and initialization. It instantiates reference, DPLL, ARM, DSP, TC, UART, USB, MMC, I2C, MCBSP, SoSSI, external, and virtual MPU clocks with CPU masks and clkdev aliases.

Important APIs/types/functions: Important pieces are the static `omap1_clk` definitions, `omap_clks[]`, `omap1_clk_init`, `omap1_clk_late_init`, `omap1_show_rates`, and global `cpu_mask`.

Control flow, state, and persistence: Init clears soft requests, computes CPU mask, stores global clock pointers, derives bootloader DPLL rate, resets DSP/idle registers, registers matching clocks, and later reprograms DPLL to the highest supported table rate from SRAM.

Dependencies and integration points: Important pieces are the static `omap1_clk` definitions, `omap_clks[]`, `omap1_clk_init`, `omap1_clk_late_init`, `omap1_show_rates`, and global `cpu_mask`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP register definitions, machine/cpu detection, common clock registration, SRAM clock code, cpufreq scaling, and board quirks such as AMS Delta BCLK inversion. Risks are large legacy clock table drift, duplicate aliases, bootloader-rate assumptions, and DPLL reprogramming fallout. Test boot rates, clkdev lookup for all platform devices, cpufreq, UART clocks, USB/MMC clocks, and OMAP_RESET_CLOCKS.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 834 lines, 27476 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock_data.c -->
