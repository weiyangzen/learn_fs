# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/Makefile

Purpose: this Makefile is the DTB build manifest for NXP/Freescale MXS i.MX23 and i.MX28 boards.

Important API surface: `dtb-$(CONFIG_ARCH_MXS)` appends 33 board DTBs. The list includes i.MX23 boards such as `imx23-evk`, `imx23-olinuxino`, `imx23-sansa`, `imx23-stmp378x_devb`, and `imx23-xfi3`; and many i.MX28 boards such as `imx28-apf28`, `imx28-apx4devkit`, `imx28-duckbill*`, `imx28-evk`, `imx28-m28evk`, `imx28-ts4600`, `imx28-tx28`, and `imx28-xea`.

Control flow: Kbuild conditionally includes the full list when `CONFIG_ARCH_MXS` is enabled. No custom commands are present.

State and persistence: the file stores the persistent build inventory for MXS DTBs. It does not affect kernel runtime state directly.

Dependencies and integration: depends on matching DTS files, `imx23-pinfunc.h`, `imx28-pinfunc.h`, and common MXS DTSI files. Parent ARM DTS Kbuild uses this fragment to produce board DTBs for packaging.

Risks and test signals: board support can disappear if a target is removed or misspelled. Test with `make ARCH=arm dtbs` for `CONFIG_ARCH_MXS`; check that each listed `.dtb` has a corresponding source.
