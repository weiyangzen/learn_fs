# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2q.c

Purpose: Berlin BG2Q descriptor driver for SoC and system-manager pinmux blocks.

Important APIs/types/functions: `berlin2q_soc_pinctrl_groups` and `berlin2q_sysmgr_pinctrl_groups` list large G/GAV/GSM mux tables. `berlin2q_pinctrl_match` binds `marvell,berlin2q-soc-pinctrl` and `marvell,berlin2q-system-pinctrl`; probe delegates to the shared Berlin core.

Control flow: platform match chooses descriptor data; common core builds unique functions from all group functions, maps function-to-groups, parses DT `function` and `groups`, and writes register fields through regmap.

State and persistence: this file is immutable descriptor data. Hardware syscon registers retain mux values across driver calls until reset or later writes.

Dependencies/integration: integrates media/audio/storage/network peripherals through DT pin states, including NAND/MMC, LVDS, RGMII, JTAG, TWSI, SPI, SATA, I2S, PDM, camera, demod, AVIF, smartcard, SD, HDMI, LEDs, UART, and EDDC.

Risks: BG2Q has many overlapping debug and peripheral functions sharing mux values; careless DT grouping can request incompatible muxes for adjacent fields. Since the Berlin core has no conflict log, later states can overwrite earlier selections.

Test signals: build with `MACH_BERLIN_BG2Q`, enumerate debugfs groups/functions, apply representative audio/video/storage pin states, and verify regmap writes use correct offsets from 0x18 through 0x40 ranges.
