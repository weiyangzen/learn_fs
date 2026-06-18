# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.c

## Purpose
`ccu-sun4i-a10.c` is the CCU/CCM provider for older Allwinner A10 and A20 SoCs. It models PLLs, CPU/AXI/AHB/APB clocks, AHB/APB gates, module clocks, DRAM gates, media clocks, MMC sample/output phase clocks, USB clocks and resets, and A10-versus-A20 differences under one driver.

This file is a compatibility-heavy provider: it supports two related SoCs with different available clocks and different `clk_hw_onecell_data` maps while sharing most descriptor definitions.

## Important APIs, Types, And Functions
The driver uses many sunxi-ng clock types:

- PLL descriptors include `pll-core` NKMP, `pll-audio-base` NM with sigma-delta, fractional video PLLs, VE PLL variants (`ccu_nkmp` for sun4i and `ccu_nk` for sun7i), DDR, peripheral, SATA, video1, and GPU PLLs.
- Bus clocks include HOSC gate, CPU mux with fixed predivider, AXI, AHB, APB0, APB1, and numerous AHB/APB gates.
- Module clocks cover NAND, memory stick, MMC0-3 with sample/output phase clocks, transport stream, security system, SPI, PATA, IR, I2S/AC97/SPDIF, keypad, SATA, USB OHCI/PHY, DRAM gates, display engine front/back ends, TCON, CSI, TVD/TVE, VE, codec, AVS, ACE, HDMI, GPU, MBUS, and output clocks.
- Separate `sun4i_a10_hw_clks` and `sun7i_a20_hw_clks` map shared descriptors into SoC-specific public clock ID spaces.
- `sunxi_a10_a20_ccu_resets[]` maps USB PHY, GPS, display, TV, CSI, VE, ACE, LVDS, GPU, and HDMI resets.
- `sun4i_a10_ccu_probe()` performs SoC match-data selection and early register adjustments before calling `devm_sunxi_ccu_probe()`.

## Control Flow
The platform driver matches `allwinner,sun4i-a10-ccu` and `allwinner,sun7i-a20-ccu`, using match data to select the correct `sunxi_ccu_desc`. Probe maps the MMIO region, adjusts the audio PLL register to reduce sigma-delta noise and force the 1x divider to one, then switches the AHB parent to peripheral PLL6 instead of CPU/AXI to avoid cpufreq-induced AHB rate changes. It then registers clocks and resets through the shared sunxi-ng probe path.

Runtime flow is generic CCF/reset-controller behavior. Consumers request rates and gates; sunxi-ng ops program factor clocks, muxes, dividers, phases, and gate bits. Reset users manipulate the mapped reset bits.

## State And Persistence
Hardware state includes all PLL factors, mux selections, divider and phase settings, gates, and reset bits. Probe performs two important current-boot mutations: audio PLL analog/divider adjustment and AHB parent reparenting. Those writes are not persisted across reset but are required for stable audio and bus timing during the boot.

The file also marks DDR-related clocks such as `pll-ddr` as critical where needed, preserving essential memory clocking from generic gate disable.

## Dependencies And Integration Points
The driver depends on Linux CCF, platform, OF match data, MMIO helpers, module support, sunxi-ng common clock types, phase and SDM helpers, and binding IDs from `ccu-sun4i-a10.h`. It imports the `SUNXI_CCU` namespace.

Integration points include CPU/AXI/AHB/APB fabric, DRAM, MMC/SD, NAND/MS/PATA/SATA storage, USB host/PHY, Ethernet/GMAC on A20, audio codec/I2S/SPDIF/AC97, timers and high-speed timer via AHB stability, display engine/TCON/HDMI/TV/CSI/video, GPU, security engine/ACE, UART/I2C/SPI/CAN/SCR/PS2, GPIO/PIO, and output clock pins.

## Risks
A10 and A20 are similar but not identical. Wrong SoC-specific clock map selection can expose clocks that do not exist or omit clocks that do. The probe-time AHB parent write uses undocumented A10 bits and is required to decouple AHB from cpufreq; changing it can break timers or peripherals when CPU frequency changes.

Audio PLL sigma-delta configuration is sensitive to audible artifacts. MMC phase clocks, display/video fractional PLLs, and DRAM gates require exact factor and phase modeling. Reset bits for display, USB PHY, GPU, HDMI, and VE can affect large subsystems and should be tested on real boards.

## Test Signals
Basic signals include successful probe for both A10 and A20 compatibles, populated `clk_summary`, no registration failures, and correct SoC-specific clock IDs. Runtime validation should cover CPU frequency changes without AHB/HS timer drift, audio output via I2S/SPDIF, MMC timing, USB PHY resets, display/HDMI/TCON paths, DRAM stability, storage buses, serial buses, GPU/video blocks, and reset-controller operation for representative resets.
