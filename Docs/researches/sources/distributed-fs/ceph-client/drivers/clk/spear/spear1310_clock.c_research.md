# sources/distributed-fs/ceph-client/drivers/clk/spear/spear1310_clock.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1310_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/spear1310_clock.c

Purpose: initializes the full SPEAr1310 clock tree from already mapped MISC and RAS register bases. It registers fixed oscillators, PLL/VCO clocks, bus roots, synthesizers, muxes, gates, and clkdev aliases for on-chip devices and RAS peripherals.

Important APIs and control flow: `spear1310_clk_init()` creates fixed-rate oscillators, GMII and I2S pad clocks, RTC gate, VCO parent muxes, VCO/PLL pairs for PLL1-PLL4, fixed PLL5/PLL6, VCO divided clocks, thermal/DDR/CPU/watchdog/TWD/AHB/APB clocks, GPT mux/gates, and numerous synthesizer-backed peripheral clocks. It uses `clk_register_vco_pll()`, `clk_register_aux()`, `clk_register_frac()`, standard mux/gate/fixed-factor helpers, and `clk_register_clkdev()` for device-name lookup. RAS-specific registration covers generic synthesizers, gated oscillator/PLL/bus clocks, CAN, SMII/RGMII Ethernet clocks and PHY muxes, UART1-5, I2C1-7, SSP1, PCI, and TDM1/2.

State and persistence behavior: persistent hardware state is in MISC and RAS clock configuration and enable registers. Software state is the global `_lock` spinlock shared by MMIO clock operations plus allocated clock wrappers from helper registration functions. The function does not use devm and does not provide rollback; it assumes one-time early init.

Dependencies and integration points: depends on board/platform code passing valid `misc_base` and `ras_base`, local SPEAr helper functions, standard CCF registration helpers, clkdev lookup for legacy device names, and rate tables/mask tables defined in the file. Device integration is by hard-coded clkdev IDs such as serial, SDHCI, CF/XD, C3, Ethernet, CLCD, I2S, I2C, DMA, USB, PCIe/SATA, ADC, SPI, GPIO, CAN, PCI, and TDM.

Risks and test signals: risks include no registration error checking, manual lifetime management, hard-coded physical device names, shared-register field conflicts, table ordering assumptions in synthesizers, VCO/PLL helper quirks propagating to CPU/bus clocks, and reliance on valid RAS mappings for a large second-stage clock tree. Test signals include boot-time clock availability for every clkdev alias, CPU/AHB/APB rate sanity, PLL/VCO rates from sysfs/debugfs, GPT/serial/SDHCI/GMAC/CLCD/I2S/ADC operation, RAS Ethernet/UART/I2C/PCI/TDM function, and no MMIO faults during early clock init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1310_clock.c -->
