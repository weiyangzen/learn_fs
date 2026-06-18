# sources/distributed-fs/ceph-client/drivers/clk/mediatek/Kconfig Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/Kconfig

### Purpose
This Kconfig file is the central build-selection surface for MediaTek common clock drivers. It exposes the shared MediaTek clock core, optional FHCTL support, and many SoC/topology-specific clock driver symbols for application processors, routers, multimedia islands, camera/image/video blocks, audio, GPU/mfg, I2C wrappers, storage, and other subsystems.

### Important APIs, Types, And Functions
Primary shared symbols are `COMMON_CLK_MEDIATEK` and `COMMON_CLK_MEDIATEK_FHCTL`. SoC roots include MT2701, MT2712, MT6735, MT6765, MT6779, MT6795, MT6797, MT7622, MT7629, MT7981, MT7986, MT7988, MT8135, MT8167, MT8173, MT8183, MT8186, MT8188, MT8192, MT8195, MT8196, MT8365, and MT8516. Subsystem symbols select or depend on their SoC roots and cover MMSYS, IMGSYS, VDEC/VENC, CAMSYS, AUDSYS, MFGCFG, VPPSYS, VDOSYS, WPESYS, IPESYS, IMP_IIC_WRAP, and related blocks.

### Control Flow, State, And Persistence
The menu is visible for `ARCH_MEDIATEK || COMPILE_TEST`. Root SoC symbols select `COMMON_CLK_MEDIATEK`; some newer or FHCTL-capable SoCs also select `COMMON_CLK_MEDIATEK_FHCTL`. Subsystem symbols generally depend on their root SoC symbol and often default to that root so a platform build pulls in the expected clock islands. Several display/camera/video symbols depend on VPPSYS or IMGSYS roots, encoding subsystem hierarchy in Kconfig rather than C code.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates with the MediaTek clock Makefile, reset-controller selection through the common core, architecture defaults for ARM/ARM64, COMPILE_TEST coverage, and DT compatibles implemented by the corresponding C files. Risks include inconsistent bool/tristate choices, default `m` subsystem clocks when built-in consumers need them early, dependency chains that omit required multimedia parents, typo-level help text or indentation issues, and enabling FHCTL only on SoCs that need it. Test signals include allmodconfig/allyesconfig, per-SoC defconfigs, module vs built-in link tests, DT boot on each SoC family, and clock/reset provider availability for subsystem devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/Kconfig -->
