# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Kconfig

Purpose: Kconfig menu for MediaTek bus interconnect drivers, centered on DVFSRC-backed EMI bandwidth voting.

Important APIs/types/functions: defines `INTERCONNECT_MTK`, `INTERCONNECT_MTK_DVFSRC_EMI`, and SoC symbols `INTERCONNECT_MTK_MT8183`, `INTERCONNECT_MTK_MT8195`, `INTERCONNECT_MTK_MT8196`.

Control flow: base symbol depends on `ARCH_MEDIATEK || COMPILE_TEST`; the EMI helper depends on `MTK_DVFSRC`; SoC drivers depend on the helper.

State and persistence: persistent `.config` selections determine compiled modules.

Dependencies/integration: MediaTek DVFSRC, directory Makefile, and common EMI probe/remove helper.

Risks and test signals: test modular and built-in dependency combinations, especially with `MTK_DVFSRC`, and ensure each SoC symbol maps correctly in the Makefile.
