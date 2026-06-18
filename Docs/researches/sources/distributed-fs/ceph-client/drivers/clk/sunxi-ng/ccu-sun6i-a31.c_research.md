# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.c

## Purpose

This file is the Common Clock Framework provider for the Allwinner A31/A31s main CCU. It models PLL roots, CPU/AHB/APB bus clocks, peripheral bus gates, storage and MMC phase clocks, display/media clocks, DRAM and MBUS clocks, GPU clocks, external clock outputs, and reset lines.

## Important APIs, types, and functions

The file is mostly declarative CCU data built with `SUNXI_CCU_*` macros and explicit `struct ccu_div`, `struct ccu_mp`, and `struct ccu_common` objects. Key tables are `sun6i_a31_ccu_clks`, `sun6i_a31_hw_clks`, `sun6i_a31_ccu_resets`, and `sun6i_a31_ccu_desc`. The entry point is `sun6i_a31_ccu_probe()`, bound by compatible `allwinner,sun6i-a31-ccu`, and registered through `module_platform_driver()`.

## Control flow, state, and persistence

Probe maps the CCU register block, forces PLL-Audio-1x divider bits to 1x, forces the MIPI PLL into MIPI mode, forces AHB1 to PLL6/prediv 3, then calls `devm_sunxi_ccu_probe()`. After registration it installs `sun6i_a31_cpu_nb`, a CPU mux notifier that temporarily bypasses CPU clocking to the 24 MHz oscillator during CPU PLL rate changes. Runtime state is hardware register state plus devm-managed CCF/reset registrations; there is no persistent storage beyond register values until reset.

## Dependencies and integration points

The driver depends on the sunxi-ng CCU helpers (`ccu_common`, gate/div/mp/mult/mux/nk/nkm/nkmp/nm/phase/sdm/reset) and binding IDs from `ccu-sun6i-a31.h`. It integrates with DT clock/reset consumers across MMC/NAND/SPI/I2C/UART, USB PHY/OHCI/EHCI/OTG, display back/front ends, LCD, HDMI, MIPI DSI/CSI, CSI, VE, GPU, codec/SPDIF/digital mic/DAUDIO, DRAM, MBUS, and external clock-output users.

## Risks and test signals

Risks concentrate in parent ordering, register bit positions, and the forced pre-probe register writes. The MIPI mode write clears mode-related bits, and mistakes there can break DSI/CSI. Audio PLL SDM intentionally hardcodes the variable divider, so rate-name mismatches are expected but exact audio rates must be checked. Test with A31/A31s boot, `clk_summary`, cpufreq transitions, MMC sampling/output phase tuning, display/HDMI/MIPI paths, USB PHYs, audio sample-rate clocks, and reset-controlled peripheral probe/unbind.
