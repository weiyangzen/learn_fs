# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/Makefile

Purpose: large Kbuild manifest for NXP/Freescale i.MX ARM DTBs and selected overlays. It covers legacy i.MX1/i.MX25/i.MX27 through i.MX7ULP and i.MXRT boards.

Important APIs/types/functions: `dtb-$(CONFIG_SOC_IMX*) +=` blocks conditionally list DTB targets by SoC family. The file also defines overlay composition variables such as `imx53-qsb-hdmi-dtbs := imx53-qsb.dtb imx53-qsb-hdmi.dtbo` and several `imx6qdl-dhcom-...-dtbs :=` combinations. It lists more than 400 DTB/DTBO target names, with the largest block under `CONFIG_SOC_IMX6Q`.

Control flow: Kbuild evaluates SoC config symbols and adds matching DTB targets. For composed overlay targets, Kbuild uses the `*-dtbs` variables to combine base DTBs with overlay DTBOs.

State and persistence: no runtime state. Persistent artifacts are generated DTBs and DTBOs, including composed overlay outputs where configured.

Dependencies and integration: depends on i.MX SoC Kconfig symbols, all referenced `.dts` and `.dtso` files, the device tree compiler, and the NXP parent `subdir-y` entry. It is the build integration point for a very large board support matrix.

Risks: high churn and many similarly named boards create risks of stale filenames, missing overlay components, and incorrect conditional grouping. A target can compile in one SoC config but be invisible in another if placed under the wrong `CONFIG_SOC_*`. Test with broad `make ARCH=arm dtbs`, targeted builds for changed boards, overlay composition checks, and scripts comparing listed `.dtb`/`.dtbo` names to source files.
