# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx9.c

Purpose: i.MX95/i.MX9 SOF platform driver descriptor using SCMI LMM control for the M7 core running SOF.

Important APIs/types/functions: `imx95_dai[]` exposes bidirectional `sai3`. `imx95_ops_init()` clones common i.MX ops and attaches DAIs. `imx95_chip_probe()` sets SCMI LMM reset vector from the SRAM resource. `imx95_core_kick()` boots the M7 logical machine. `imx95_core_shutdown()` forcefully shuts it down. `imx95_chip_info` defines mailbox/window offsets, DMA reserved flag, SRAM memory, DAIs, and chip ops.

Control flow: OF match for `fsl,imx95-cm7-sof` supplies the generated descriptor to `sof_of_probe()`. Common i.MX probe maps SRAM and calls chip probe to program reset vector. SOF core run invokes SCMI boot; suspend/remove invoke SCMI shutdown.

State and persistence: static descriptor/chip info and common i.MX runtime data. Reset vector is programmed in platform firmware through SCMI LMM.

Dependencies and integration points: SCMI i.MX LMM driver, OF resources, SOF OF device layer, common i.MX ops, and board machine compatible `fsl,imx95-19x19-evk`.

Risks: only one DAI is declared. `has_dma_reserved` is true while memory regions list only non-reserved SRAM, so device tree must still provide a reserved `dma` region for common probe. SCMI service availability is mandatory.

Test signals: i.MX95 OF probe, reset-vector programming, SCMI boot/shutdown, firmware mailbox offsets, topology `sof-imx95-wm8962.tplg`, and SAI3 PCM operation.
