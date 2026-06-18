# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs.c

Purpose: This file implements the PolarFire SoC MSS/core complex clock controller. It registers the MSS PLL internal clock, four MSS PLL outputs, CPU/AXI/AHB/RTC reference dividers, and peripheral gate clocks.

Important APIs, types, and functions: Key types are `mpfs_clock_data`, `mpfs_msspll_hw_clock`, `mpfs_msspll_out_hw_clock`, `mpfs_cfg_hw_clock`, and `mpfs_periph_hw_clock`. Important functions include `mpfs_clk_msspll_recalc_rate`, `mpfs_clk_register_mssplls`, `mpfs_clk_register_msspll_outs`, `mpfs_cfg_clk_recalc_rate`, `mpfs_cfg_clk_determine_rate`, `mpfs_cfg_clk_set_rate`, peripheral gate callbacks, `mpfs_clk_syscon_probe`, `mpfs_clk_old_format_probe`, and `mpfs_clk_probe`.

Control flow: Probe first tries the modern syscon layout using `microchip,mpfs-mss-top-sysreg` plus an MSS PLL resource. If that fails, it falls back to an older device-tree format with two mapped resources, creates an MMIO regmap, and registers the MPFS reset controller. It then registers PLLs, outputs, config dividers, peripheral gates, and an OF onecell provider.

State and persistence behavior: Hardware registers hold PLL, divider, gate, and reset state. The driver stores a regmap, MMIO bases, and onecell clock array. Several peripheral gates are marked `CLK_IS_CRITICAL`, including ENVM, MMUART0, RTC, DDRC, FIC clocks, and Athena, because firmware, memory, RTC, or fabric interconnects depend on them.

Dependencies and integration points: It depends on CCF, regmap, syscon, platform resources, MPFS reset-controller helpers, dt-binding IDs, and `soc/microchip/mpfs.h`. Peripheral consumers are Microchip MPFS device-tree nodes for MAC, MMC, UART, SPI, I2C, CAN, USB, RTC, QSPI, GPIO, DDR, FIC, and CFM.

Risks and edge cases: `regmap_update_bits` in `mpfs_cfg_clk_set_rate` appears to pass value and mask in reversed order, so rate programming deserves careful review. PLL reference divider values must not be zero. Old/new DT fallback changes reset-controller behavior. Test signals include modern and old DT probing, critical clocks staying enabled, CPU/AXI/AHB divider rate changes, peripheral gate enable/disable, reset controller registration in old format, and dt-binding ID coverage.
