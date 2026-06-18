# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2.c

Purpose: Marvell Berlin BG2 pinctrl descriptor driver for SoC and system-manager pinmux blocks.

Important APIs/types/functions: static `berlin2_soc_pinctrl_groups` and `berlin2_sysmgr_pinctrl_groups` describe register offsets, bit widths, LSB positions, and legal mux functions. `berlin2_pinctrl_match` maps `marvell,berlin2-soc-pinctrl` and `marvell,berlin2-system-pinctrl` to descriptor data. Probe delegates to `berlin_pinctrl_probe()`.

Control flow: the builtin platform driver matches DT, retrieves `device_get_match_data()`, and lets the shared Berlin core build function/group state and use the parent syscon regmap.

State and persistence: all mux state is in syscon registers addressed by the descriptor offsets. This file owns no mutable runtime state beyond constants.

Dependencies/integration: depends on the Berlin core, OF match data, platform bus, and parent syscon regmap. Functions span GPIO, SPI, USB debug, SATA, SD, UART, TWSI, HDMI, I2S, PDM, NAND/eMMC, Ethernet, LEDs, and AV output signals.

Risks: duplicate mux values intentionally expose one hardware mode under multiple function names for DT composition; edits must preserve those aliases. Register bit-width/LSB errors can affect unrelated pins in the same syscon word.

Test signals: boot BG2 DTs for both compatible strings, inspect generated function groups in debugfs, and verify representative mux writes in the parent syscon.
