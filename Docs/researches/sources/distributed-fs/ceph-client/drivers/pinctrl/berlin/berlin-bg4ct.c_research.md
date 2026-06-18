# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg4ct.c

Purpose: Berlin4CT descriptor driver for SoC, AVIO, and system pinctrl MMIO blocks.

Important APIs/types/functions: `berlin4ct_soc_pinctrl_groups`, `berlin4ct_avio_pinctrl_groups`, and `berlin4ct_sysmgr_pinctrl_groups` define mux tables. Unlike older BG2 drivers, `berlin4ct_pinctrl_probe()` maps its own MMIO resource and creates a regmap with 32-bit registers and stride 4 before calling `berlin_pinctrl_probe_regmap()`.

Control flow: match data selects one descriptor for `marvell,berlin4ct-soc-pinctrl`, `marvell,berlin4ct-avio-pinctrl`, or `marvell,berlin4ct-system-pinctrl`. Probe maps resource 0, initializes regmap, and hands both to the common core.

State and persistence: mux state is MMIO register state in each block. Runtime state is common-core allocation only; this file has static descriptors.

Dependencies/integration: depends on OF, platform MMIO resources, regmap-mmio, and Berlin core. Functions cover NAND, RGMII, SD, STS, smartcard, SPI, USB VBUS, TWI, AVIO audio/HDMI/PDM, system UART/JTAG/SPI/LED/HDMI pins.

Risks: resource-size-based `max_register` must match hardware register span. Some groups use high mux values for debug functions; bad DT can route board-critical storage/network pins incorrectly.

Test signals: boot each of the three compatible blocks, verify regmap creation, use debugfs to confirm group counts, and observe register changes for NAND/RGMII and AVIO I2S pin states.
