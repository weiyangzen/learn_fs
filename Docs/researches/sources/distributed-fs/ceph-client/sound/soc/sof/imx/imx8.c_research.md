# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx8.c

Purpose: i.MX8-family SOF platform driver descriptors, DAI tables, memory maps, and chip-specific DSP boot/reset controls for i.MX8, i.MX8X, i.MX8M, and i.MX8ULP.

Important APIs/types/functions: chip ops include `imx8_run()`, `imx8x_run()`, `imx8_shutdown()`, `imx8m_reset()`, `imx8m_run()`, `imx8ulp_reset()`, and `imx8ulp_run()`. Probe helpers obtain SCU IPC, DAP/runstall reset, or syscon regmap. DAI arrays cover ESAI/SAI/MICFIL variants. `imx8_ops_init()` clones `sof_imx_ops`, adds Xtensa debug dump/arch ops, and attaches chip DAIs. `IMX_SOF_DEV_DESC()` creates descriptors for each compatible.

Control flow: OF match selects a descriptor by DSP compatible. Common probe maps memory/enables clocks then chip probe stores chip private control handles. Firmware loading occurs while the core is stalled/reset; core kick releases stall or starts CPU through SCU/syscon/SMC path depending on SoC. Machine selection uses board-compatible entries to choose topology and `asoc-audio-graph-card2`.

State and persistence: chip private data is SCU IPC handle, `imx8m_chip_data`, or regmap in `imx_common_data.chip_pdata`. Static chip info records IPC mailbox offsets, memory regions, DMA reserved flag for ULP, DAIs, and ops.

Dependencies and integration points: i.MX SCU services, ARM SMCCC, syscon/regmap, reset controls, OF machine matching, SOF OF probe/remove/PM, Xtensa debug support, and common i.MX ops.

Risks: boot control is SoC-specific and fragile: incorrect offset controls or reset/stall order can prevent firmware boot. Hard-coded DAP debug address is used for i.MX8M. ULP uses SMC return value for XRDC setup. Board-compatible topology selection must match device trees.

Test signals: OF probe for each compatible, firmware boot/kick/reset, topology selection per board compatible, panic dump, and DAI registration for SAI/ESAI/MICFIL.
