# subset-b-005471 research

This grouped report covers UFS host controller build glue and vendor drivers under `sources/distributed-fs/ceph-client/drivers/ufs/host`. Each section preserves the original source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/Kconfig

## Purpose
Defines kernel configuration switches for UFS host controller transport glue and vendor-specific platform drivers. It decides which UFS host modules are buildable and records architecture, bus, PM, reset, and crypto feature dependencies.

## Important symbols and APIs
Key symbols in this subset are `SCSI_UFS_DWC_TC_PCI`, `SCSI_UFS_DWC_TC_PLATFORM`, `SCSI_UFS_CDNS_PLATFORM`, `SCSI_UFS_TI_J721E`, `SCSI_UFS_EXYNOS`, `SCSI_UFS_VARIABLE_SG_ENTRY_SIZE`, `SCSI_UFS_HISI`, `SCSI_UFS_MEDIATEK`, and `SCSI_UFS_AMD_VERSAL2`. Base dependencies are `SCSI_UFSHCD_PCI` for PCI controllers and `SCSI_UFSHCD_PLATFORM` for MMIO/platform controllers.

## Control flow and state
There is no runtime control flow or persistence. The file contributes build-time state through Kconfig dependency resolution. Selecting a vendor option enables the corresponding Makefile object and therefore registers platform or PCI drivers at module load.

## Dependencies and integration points
The symbols integrate with `drivers/ufs/host/Makefile`, the Linux UFSHCD core, device tree match tables, and arch configuration. Some symbols intentionally restrict to real SoC families unless `COMPILE_TEST` is allowed. MediaTek selects `PHY_MTK_UFS` and `RESET_TI_SYSCON`; Qualcomm selects inline crypto engine support when UFS crypto is enabled.

## Risks and test signals
Main risks are missing dependency declarations that allow unusable compile combinations, or too-strict arch dependencies that block compile testing. Test signals are `allyesconfig`, `allmodconfig`, and targeted builds for each selected driver, especially combinations with `SCSI_UFS_CRYPTO`, `COMPILE_TEST`, and architecture-specific reset or PHY providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/Makefile

## Purpose
Maps UFS host Kconfig symbols to object files. It composes shared DesignWare glue with Synopsys G210 and AMD Versal2 drivers and builds each vendor platform module when its configuration symbol is enabled.

## Important APIs and build objects
The file uses standard kernel `obj-$(CONFIG_...) += ...` assignments. Notable composite entries are `SCSI_UFS_DWC_TC_PCI` and `SCSI_UFS_DWC_TC_PLATFORM`, which include `ufshcd-dwc.o` and `tc-dwc-g210.o`, and `SCSI_UFS_AMD_VERSAL2`, which includes `ufs-amd-versal2.o ufshcd-dwc.o`. Single-object entries include `cdns-pltfrm.o`, `ufs-exynos.o`, `ufs-hisi.o`, `ufs-mediatek.o`, and `ti-j721e-ufs.o`.

## Control flow and state
There is no runtime state. Build flow is entirely declarative: selected Kconfig symbols produce built-in or module objects, and object ordering matters for linked modules that need exported helper functions.

## Dependencies and integration points
The file is tightly coupled to Kconfig symbols and source filenames in the same directory. It also exposes the expectation that common DWC helper code can be linked into multiple driver modules.

## Risks and test signals
Risks include stale object names, missing shared objects for drivers that call helper symbols, and accidental multiple-definition issues when shared helpers are included in built-in combinations. Test signals are kernel builds for each symbol as `y` and `m`, plus `modpost` checks for exported Synopsys helper symbols and DWC helper references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/cdns-pltfrm.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/cdns-pltfrm.c

## Purpose
Implements Cadence UFSHCI platform variant operations on top of the generic `ufshcd-pltfrm` driver. It programs controller timing, handles a Cadence hibern8 quirk by saving L4 DME attributes, disables host TX LCC before startup, and provides an optional M31 16nm PHY register tweak.

## Important APIs, types, and functions
`struct cdns_ufs_host` stores 12 transport-layer attributes. `cdns_ufs_get_l4_attr()` and `cdns_ufs_set_l4_attr()` snapshot and restore `T_*` MIBs. `cdns_ufs_set_hclkdiv()` locates `core_clk`, derives the HCLK divider in MHz, writes `CDNS_UFS_REG_HCLKDIV`, and reads back to flush the write. `cdns_ufs_hce_enable_notify()`, `cdns_ufs_link_startup_notify()`, and `cdns_ufs_hibern8_notify()` are wired through `ufs_hba_variant_ops`. `cdns_ufs_m31_16nm_phy_initialization()` sets bit 24 in `CDNS_UFS_REG_PHY_XCFGD1`.

## Control flow and state
Probe matches `cdns,ufshc` or `cdns,ufshc-m31-16nm`, selects variant ops from match data, then calls `ufshcd_pltfrm_init()`. Runtime state is only the devm-allocated variant struct and cached L4 attributes. On pre-HCE enable it writes HCLKDIV; on pre-link it disables LCC and AH8; before hibern8 enter it saves L4 attributes and after hibern8 exit it restores them.

## Dependencies and integration points
Depends on UFSHCD core DME helpers, platform probing, Linux clock framework, OF match data, and `ufshcd-pltfrm` PM callbacks. It integrates with UIC notification sequencing supplied by UFSHCD core.

## Risks and test signals
Risk centers on missing `core_clk`, wrong clock rate units, DME get/set failures being ignored in L4 save/restore, and AH8 being forcibly disabled. Test signals are successful link startup, no unexpected interrupts after AH8 disable, HCLKDIV matching `core_clk / 1000000`, and suspend/resume or hibern8 cycles preserving L4 connectivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/cdns-pltfrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pci.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pci.c

## Purpose
Provides PCI glue for the Synopsys DesignWare UFS G210 test chip. It binds Synopsys PCI device IDs, chooses the 20-bit or 40-bit PHY initialization routine from a module parameter, maps BAR0, allocates a UFS host, and starts UFSHCD.

## Important APIs, types, and functions
`tc_type` is a module parameter accepting `20` or `40`. `tc_dwc_g210_pci_hba_vops` names the variant and uses `ufshcd_dwc_link_startup_notify`; probe mutates its `phy_initialization` pointer to `tc_dwc_g210_config_20_bit()` or `tc_dwc_g210_config_40_bit()`. `tc_dwc_g210_pci_probe()` uses `pcim_enable_device()`, `pci_set_master()`, `pcim_iomap_region()`, `ufshcd_alloc_host()`, and `ufshcd_init()`. Remove calls `ufshcd_remove()` after disabling runtime PM.

## Control flow and state
Probe rejects unspecified chip type with `-EPERM`, then initializes the PCI device and UFS host. Persistent state is in PCI driver data established by UFSHCD and the global variant ops structure. Runtime PM is allowed after successful initialization.

## Dependencies and integration points
Depends on PCI, UFSHCD core, DesignWare helper code, G210 exported configuration functions, and generic UFS PM callbacks. It is built with `ufshcd-dwc.o` and `tc-dwc-g210.o` through the Makefile.

## Risks and test signals
The global mutable `tc_dwc_g210_pci_hba_vops` is simple but assumes all probed devices use the same module parameter. Incorrect `tc_type` prevents probing or applies the wrong DME table. Test signals are successful probe for PCI IDs `0xB101`/`0xB102`, correct log line for 20-bit or 40-bit RMMI, link startup completion, and clean runtime PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pltfrm.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pltfrm.c

## Purpose
Provides OF/platform glue for the Synopsys G210 test chip. Unlike the PCI version, chip width is selected by device-tree compatible string rather than a module parameter.

## Important APIs, types, and functions
Two `ufs_hba_variant_ops` instances select `tc_dwc_g210_config_20_bit()` or `tc_dwc_g210_config_40_bit()` while sharing `ufshcd_dwc_link_startup_notify()`. `tc_dwc_g210_pltfm_match` maps `snps,g210-tc-6.00-20bit` and `snps,g210-tc-6.00-40bit`. Probe retrieves match data with `of_match_node()` and calls `ufshcd_pltfrm_init()`. Remove delegates to `ufshcd_pltfrm_remove()`.

## Control flow and state
The generic platform UFSHCD driver owns the host lifetime. This file contributes variant ops at probe time and uses standard UFS system/runtime PM callbacks. There is no private persistent state.

## Dependencies and integration points
Depends on OF matching, `ufshcd-pltfrm`, `ufshcd-dwc`, and the shared G210 DME setup functions. It integrates at the UFSHCD variant-op boundary.

## Risks and test signals
Risks are mostly device-tree binding accuracy and correct use of match data; a missing or wrong compatible string selects no PHY setup. Test signals are correct compatible matching, link startup notification reaching DesignWare glue, successful G210 PHY configuration, and platform suspend/resume through UFSHCD PM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pltfrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.c

## Purpose
Contains the shared Synopsys G210 test-chip PHY setup sequences. It writes local DME attributes required for 20-bit and 40-bit RMMI modes and exports the two configuration functions used by PCI and platform glue.

## Important APIs, types, and functions
`tc_dwc_g210_setup_40bit_rmmi()` and `tc_dwc_g210_setup_20bit_rmmi()` apply static `struct ufshcd_dme_attr_val` tables through `ufshcd_dwc_dme_set_attrs()`. The 20-bit path is split into lane 0 and conditional lane 1 setup; lane 1 is programmed only when `PA_AVAILRXDATALANES` or `PA_AVAILTXDATALANES` report two lanes. Public exports are `tc_dwc_g210_config_40_bit()` and `tc_dwc_g210_config_20_bit()`, which apply the setup, write `VS_MPHYCFGUPDT`, then enable `VS_DEBUGOMC`.

## Control flow and state
No heap state is maintained. The functions program hardware state via DME writes. Errors from attribute programming stop the sequence; update/debug writes are checked enough to propagate failures.

## Dependencies and integration points
Depends on UFS UniPro MIB definitions, DesignWare UFS helper attributes, and UFSHCD DME access. PCI and platform drivers call these functions from their `.phy_initialization` variant op.

## Risks and test signals
The tables are hardware magic values; incorrect values can break link training or marginal signal behavior. Lane discovery errors are not independently logged. Test signals are successful DME write sequences, correct lane count behavior, link startup across 1-lane and 2-lane configurations, and logs showing the expected RMMI width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.h

## Purpose
Declares the shared Synopsys G210 PHY configuration entry points used by PCI and platform glue.

## Important APIs and types
Forward declares `struct ufs_hba` and exposes `tc_dwc_g210_config_40_bit(struct ufs_hba *hba)` and `tc_dwc_g210_config_20_bit(struct ufs_hba *hba)`.

## Control flow and state
There is no runtime behavior or persistent state in this header. It defines the compile-time contract between transport glue and the shared configuration implementation.

## Dependencies and integration points
Included by `tc-dwc-g210.c`, `tc-dwc-g210-pci.c`, and `tc-dwc-g210-pltfrm.c`. It intentionally avoids including full UFSHCD headers by forward declaration, keeping the interface small.

## Risks and test signals
Risks are ABI-level within the module build: changing prototypes without updating all users breaks compilation or exported symbol use. Test signals are clean builds for both PCI and platform G210 options and successful modpost resolution of exported functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ti-j721e-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ti-j721e-ufs.c

## Purpose
Implements the TI J721E UFS subsystem glue layer that prepares a Cadence UFS controller child. It programs subsystem control bits for MPHY reference clock frequency and PCS reset, then populates child platform devices.

## Important APIs, types, and functions
`struct ti_j721e_ufs` stores the mapped subsystem register base and the control register value to restore on resume. `ti_j721e_ufs_probe()` uses `devm_platform_ioremap_resource()`, runtime PM, `devm_clk_get()`, `clk_get_rate()`, `writel()`, and `of_platform_populate()`. `ti_j721e_ufs_resume()` rewrites the cached control value. Remove depopulates children and disables runtime PM.

## Control flow and state
Probe allocates private state, maps registers, resumes the device, detects a 26 MHz MPHY clock, sets `TI_UFS_SS_CLK_26MHZ` when needed, deasserts PCS reset via `TI_UFS_SS_RST_N_PCS`, stores drvdata, and creates child devices. Persistent state is the cached `reg` field used for sleep resume.

## Dependencies and integration points
Depends on OF platform population, runtime PM, clock framework, and a downstream child node that normally binds the Cadence UFS controller. The Kconfig description makes this a glue layer, not the UFSHCD host itself.

## Risks and test signals
Risks include incorrect refclk detection for non-26 MHz inputs, child population failure after PM enable, and lost subsystem register state across suspend. Test signals are child Cadence probe success, correct `TI_UFS_SS_CTRL` value before and after resume, and balanced runtime PM on probe failure and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ti-j721e-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-amd-versal2.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-amd-versal2.c

## Purpose
Implements AMD Versal Gen 2 UFS platform support on top of DesignWare UFSHCD. It handles resets, firmware-mediated calibration readiness, PHY register access through DME sideband registers, PHY enable, and power-mode-specific rate/adaptation programming.

## Important APIs, types, and functions
`struct ufs_versal2_host` stores reset controls, host clock rate, PHY mode, and ATT/CTLE calibration bytes read from firmware. `ufs_versal2_phy_reg_read()` and `_write()` access PHY registers through `CBCREG*` MIBs and `VS_MPHYCFGUPDT`. `ufs_versal2_phy_init()` waits for `zynqmp_pm_is_mphy_tx_rx_config_ready()`, programs RMMI attributes, deasserts PHY reset, waits for SRAM init, applies calibration, and enables MPHY FSMs. `ufs_versal2_pwr_change_notify()` handles fallback to slow mode when no calibration exists, selects HS rate, toggles RX override/ack, and configures initial adapt for 2-lane HS.

## Control flow and state
`ufs_versal2_init()` allocates the variant state, records the `core` clock rate, obtains and asserts host/PHY resets, asks firmware to bypass SRAM, deasserts host reset, reads calibration values, and sets `UFSHCD_QUIRK_SKIP_DEF_UNIPRO_TIMEOUT_SETTING`. HCE post-change initializes PHY; link pre-change writes `DWC_UFS_REG_HCLKDIV`; link post-change delegates to DWC startup notification.

## Dependencies and integration points
Depends on ZynqMP firmware APIs, reset controller, clock list naming, DesignWare UFS MIB definitions, UFSHCD platform probing, and UniPro power attributes.

## Risks and test signals
Risks include firmware readiness timeout, missing calibration forcing slow mode, incorrect clock name `core`, reset ordering, and polling loops with one-second microsecond counters. Test signals are firmware calls succeeding, TX/RX FSMs reaching Hibern8/Sleep/LSBurst, link startup with correct HCLKDIV, HS mode only on calibrated parts, and successful suspend/runtime PM through UFSHCD callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-amd-versal2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-exynos.c

## Purpose
Implements Samsung Exynos, ExynosAuto, Tesla FSD, and Google GS101 UFSHCI variant support. It owns vendor HCI, UniPro, UFS Protector, PHY timing, clock gating, hibern8, crypto/FMP setup, SoC data tables, and platform probe glue.

## Important APIs, types, and functions
The central state is `struct exynos_ufs` from the header. Initialization maps `vs_hci`, `unipro`, and `ufsp`, parses SoC match data, gets `ufs-phy`, configures optional FMP crypto, applies SoC `drv_init`, reads clocks, computes PHY timing counters, and configures SMU. Core variant ops include `exynos_ufs_hce_enable_notify()`, `exynos_ufs_link_startup_notify()`, `exynos_ufs_negotiate_pwr_mode()`, `exynos_ufs_pwr_change_notify()`, `exynos_ufs_setup_clocks()`, `exynos_ufs_hibern8_notify()`, `exynos_ufs_suspend()`, and `exynos_ufs_resume()`. Crypto-specific code defines `struct fmp_sg_entry`, SMC calls, and `exynos_ufs_fmp_fill_prdt()`.

## Control flow and state
Probe chooses default or virtual-host vops from match data and calls `ufshcd_pltfrm_init()`. HCE pre-change sets segment size, runs SoC pre-HCE, resets host/link, and toggles device reset GPIO; post-change computes PWM divider, enables automatic HCI clock control, and runs SoC post-HCE. Pre-link programs fatal error interrupts, APB clock divider, UniPro attributes, SoC link hooks, PHY init, and PHY timing/capability attributes. Post-link establishes CPort connection, configures interrupt aggregation, PRDT size, nexus type bits, AXI burst, optional hibern8 timing override, PHY calibration, and SoC post-link. Hibern8 notify gates/ungates clocks and optionally enforces a software hibern8 timer. Resume reconfigures SMU and FMP.

## Dependencies and integration points
Depends on UFSHCD core variant ops, PHY framework, OF resources, syscon/regmap for IO coherency, ARM SMCCC for secure crypto setup, block crypto profile APIs, and SoC match data. It integrates deeply with device tree resource names and UFSHCD quirks/capabilities.

## Risks and test signals
Risks include fragile magic MIB/register values, SoC-specific resource names, clock rate range failures, software hibern8 timing mistakes, FMP PRDT alignment requirements, secure monitor failures, and virtual-host mailbox timeout. Test signals include link startup on each compatible, pclk within 70-267 MHz, DMA alignment to 4096 bytes, crypto profile only when secure FMP setup succeeds, hibern8 entry/exit without clock races, suspend/resume preserving SMU/FMP state, and successful MCQ-free request/task nexus handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-exynos.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-exynos.h

## Purpose
Defines Exynos UFS vendor register offsets, UniPro debug MIBs, PHY timing attribute layouts, SoC driver-data contracts, private host state, option flags, lane iteration helpers, and MMIO accessors used by `ufs-exynos.c`.

## Important APIs, types, and functions
Important types are `struct exynos_ufs_uic_attr`, `struct exynos_ufs_drv_data`, `struct ufs_phy_time_cfg`, and `struct exynos_ufs`. Driver-data callbacks cover SoC-specific init, pre/post link, pre/post power change, HCE enable, and suspend. Option flags such as `EXYNOS_UFS_OPT_BROKEN_AUTO_CLK_CTRL`, `EXYNOS_UFS_OPT_USE_SW_HIBERN8_TIMER`, `EXYNOS_UFS_OPT_UFSPR_SECURE`, and `EXYNOS_UFS_OPT_SKIP_CONFIG_PHY_ATTR` gate behavior in the C file. Macros generate `hci_*`, `unipro_*`, and `ufsp_*` accessors.

## Control flow and state
The header itself has no runtime flow, but it defines all persistent variant state: mapped MMIO windows, PHY handle, clocks, available lanes, timing config, hibern8 timestamp, sysreg IO coherency fields, SoC data, and options.

## Dependencies and integration points
Depends on UFSHCD types, Linux PHY, clocks, regmap, and UniPro constants from included C context. It is the ABI between static SoC tables and generic Exynos variant logic.

## Risks and test signals
Risks include incorrect register offsets, stale timing constants, option flags that interact subtly, and mutable `uic_attr` tables modified during DT parse. Test signals are compile coverage for all Exynos compatibles, correct MMIO accessors, and runtime validation of lane iteration, timing computation, and SoC option combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-exynos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.c

## Purpose
Implements HiSilicon Hi3660/Hi3670 UFS platform variant support. It powers and clocks the UFS subsystem, initializes SoC sysctrl state, applies vendor UniPro/MPHY tuning, negotiates power mode, and manages suspend/resume reference clock behavior.

## Important APIs, types, and functions
`ufs_hisi_init_common()` allocates `struct ufs_hisi_host`, gets reset control, sets PM levels, and maps sysctrl resource 1. `ufs_hisi_clk_init()` and `ufs_hisi_soc_init()` sequence reference clocks, isolation, PSW power, reset, and device reset controls. `ufs_hisi_link_startup_pre_change()` writes many vendor MIBs, checks TX FSM hibern8 through `ufs_hisi_check_hibern8()`, disables AH8/LCC, and closes Mk2 extension support. `ufs_hisi_pwr_change_pre_change()` programs SaveConfigTime, sync lengths, and UniPro timeout values. Variant ops are separate for Hi3660 and Hi3670; Hi3670 sets `UFS_HISI_CAP_PHY10nm`.

## Control flow and state
Probe matches compatible data and calls `ufshcd_pltfrm_init()`. Init performs sysctrl and reset setup before link startup. Runtime state is in `struct ufs_hisi_host`, including sysctrl MMIO, reset control, capability flags, and `in_suspend`. System sleep suspend disables reference clock and records suspend state; resume restores override and ref clock.

## Dependencies and integration points
Depends on UFSHCD platform core, reset framework, OF resource layout, UniPro DME helpers, and sysctrl register macros from `ufs-hisi.h`.

## Risks and test signals
Risks are unverified DME writes, hard-coded magic MIBs, resource index dependence, and suspend behavior differing between runtime and system PM. Test signals include hibern8 FSM check passing on both lanes, link startup with AH8 disabled, Hi3670 10 nm branch behavior, correct sysctrl register transitions, and suspend/resume without reference-clock loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.h

## Purpose
Defines HiSilicon UFS sysctrl offsets, bit masks, UFS host register constants, capability flags, private state, and helper macros for sysctrl MMIO access.

## Important APIs and types
`struct ufs_hisi_host` stores the UFSHCD pointer, sysctrl base, reset control, caps, and suspend flag. Macros `ufs_sys_ctrl_writel()`, `ufs_sys_ctrl_readl()`, `ufs_sys_ctrl_set_bits()`, and `ufs_sys_ctrl_clr_bits()` implement register access. Constants cover PSW power, PHY isolation, clock gating bypass, reset, reference clock, device reset, MPHY TX FSM, AHIT mask, and `UFS_HISI_CAP_PHY10nm`.

## Control flow and state
No executable flow beyond inline-like macros. The header defines persistent state consumed by `ufs-hisi.c`, especially capability and suspend bookkeeping.

## Dependencies and integration points
Requires Linux MMIO helpers and UFSHCD/reset types via includers. It is coupled to the sysctrl resource mapped by the C file and to Hi3660/Hi3670 hardware register layout.

## Risks and test signals
Risks are wrong bit masks or register offsets causing unsafe power/reset sequencing. Because bit helpers read-modify-write without locks, callers must ensure appropriate serialization. Test signals are correct sysctrl values during init/suspend/resume and compile coverage of all macro users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-sip.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-sip.h

## Purpose
Defines the MediaTek secure monitor interface used by the UFS driver for power, reset, crypto, reference clock, SRAM, MPHY, MTCMOS, and VCC selection operations.

## Important APIs, types, and functions
`MTK_SIP_UFS_CONTROL` is the SMC function ID. Command bits include `UFS_MTK_SIP_VA09_PWR_CTRL`, `UFS_MTK_SIP_DEVICE_RESET`, `UFS_MTK_SIP_CRYPTO_CTRL`, `UFS_MTK_SIP_REF_CLK_NOTIFICATION`, `UFS_MTK_SIP_SRAM_PWR_CTRL`, `UFS_MTK_SIP_GET_VCC_NUM`, `UFS_MTK_SIP_DEVICE_PWR_CTRL`, `UFS_MTK_SIP_MPHY_CTRL`, and `UFS_MTK_SIP_MTCMOS_CTRL`. `struct ufs_mtk_smc_arg` packages SMC arguments. `_ufs_mtk_smc()` calls `arm_smccc_smc()`. Convenience macros expose each operation.

## Control flow and state
The header has inline SMC dispatch only; persistent state lives in firmware or caller-provided `arm_smccc_res`. Command wrappers are synchronous firmware calls.

## Dependencies and integration points
Depends on `linux/soc/mediatek/mtk_sip_svc.h` and ARM SMCCC definitions through includers. Used by `ufs-mediatek.c` to coordinate hardware that Linux cannot directly control.

## Risks and test signals
Risks include firmware ABI mismatch, typoed comments indicating vendor-specific command semantics, and macros that require callers to pass a real `arm_smccc_res` lvalue. Test signals are nonzero `res.a0` handling in callers, successful reset/refclk/crypto operations, and boot tests across firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-sip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-trace.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-trace.h

## Purpose
Declares MediaTek UFS tracepoints for event reporting and clock scaling decisions.

## Important APIs and tracepoints
`TRACE_SYSTEM` is `ufs_mtk`. `TRACE_EVENT(ufs_mtk_event)` records an event type and data value. `TRACE_EVENT(ufs_mtk_clk_scale)` records the clock name, scale direction, and resulting clock rate. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to this host-driver path.

## Control flow and state
There is no persistent state. When `ufs-mediatek.c` defines `CREATE_TRACE_POINTS`, these declarations generate tracepoint definitions. Runtime callers emit events through `trace_ufs_mtk_event()` and `trace_ufs_mtk_clk_scale()`.

## Dependencies and integration points
Depends on the Linux tracepoint framework. Integrated with MediaTek event notification and clock scaling code for observability without always printing logs.

## Risks and test signals
Risks are trace include path breakage when files move, format-string mismatch, and unhelpful event IDs unless correlated with UFSHCD event enums. Test signals are successful tracepoint generation, visibility under tracefs/perf, and emitted records during UIC errors and devfreq clock scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.c

## Purpose
Implements MediaTek UFSHCI platform support. It manages MediaTek-specific reset, PHY power, secure firmware calls, reference clock handshake, UniPro low-power mode, device quirks, regulators, clock scaling, MCQ interrupts, debug dumping, PM, and platform probe integration.

## Important APIs, types, and functions
Private state is `struct ufs_mtk_host` from the header. Initialization flows through `ufs_mtk_init()`, which parses DT capability booleans, initializes MCQ IRQ metadata, binds optional MPHY, gets reset controls, backs up MPHY state, enables UFSHCD capabilities, initializes private clocks, powers MPHY, handles RTFF MTCMOS, turns clocks on, and records IP version. Variant ops include HCE/link/power-change notifications, suspend/resume, event notification, devfreq scaling, MCQ resource setup, ESI config, and SCSI device config. Key helpers include `ufs_mtk_setup_ref_clk()`, `ufs_mtk_wait_idle_state()`, `ufs_mtk_wait_link_state()`, `ufs_mtk_mphy_power_on()`, `ufs_mtk_pre_pwr_change()`, `ufs_mtk_auto_hibern8_disable()`, `ufs_mtk_link_set_hpm()`, `ufs_mtk_link_set_lpm()`, `_ufs_mtk_clk_scale()`, and MCQ IRQ handlers.

## Control flow and state
Probe first creates device links to reset/PHY providers when present, then calls `ufshcd_pltfrm_init()` with MediaTek vops and forces device regulator LPM off. HCE pre-change resets host unless UniPro LPM is active, enables crypto, disables AH8 if configured, and applies IP-version-specific MMIO settings. Link pre-change disables UniPro LPM, disables LCC and deep stall, and sets selected debug OMC bits; post-link enables UniPro clock gating. Power-change pre-stage temporarily disables AH8, may use FASTAUTO transition, configures adaptation, and post-stage restores AHIT. Suspend/resume sequences UniPro LPM/HPM, MPHY power, SRAM power, regulator LPM, MTCMOS, and clock scaling.

## Dependencies and integration points
Depends on UFSHCD platform/core, MediaTek SIP firmware ABI, reset framework, regulators, clock framework, PHY framework, OF device links, Linux tracepoints, MCQ core APIs, block multiqueue CPU mappings, and UFS device quirk infrastructure.

## Risks and test signals
Risks include firmware ABI failures, refclk ack timeout, AH8/link-state races, static AHIT backup during power change, optional reset pointers used in reset sequence, MCQ IRQ topology assumptions, regulator LPM policy for broken VCC devices, and resume returning success after recovery to avoid I/O hangs. Test signals include successful boot on MT8183/MT8195 compatibles, refclk ack transitions, UIC error tracepoints, MCQ queue interrupts and affinity, clock scaling parent changes plus vcore requests, suspend/resume under runtime and system PM, and device-specific quirk application for Samsung, Micron, SK hynix, Toshiba, and UFS 5.0 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.h

## Purpose
Defines MediaTek UFS vendor register offsets, MCQ constants, refclock controls, UniPro vendor attributes, capability flags, private clock/crypto/MCQ state structures, runtime constants, and IP version identifiers.

## Important APIs and types
Important constants include `REG_UFS_REFCLK_CTRL`, `REG_UFS_MMIO_OPT_CTRL_0`, `REG_UFS_MTK_IP_VER`, debug/probe registers, MCQ SQ/CQ offsets, `REFCLK_REQUEST`, `REFCLK_ACK`, and `REFCLK_REQ_TIMEOUT_US`. Capability flags include boost crypto, VA09 power control, AH8 disable, broken VCC, VCCQx LPM allowance, FASTAUTO power-mode change, TX skew fix, MCQ disable, RTFF MTCMOS, and broken RTC. Types include `struct ufs_mtk_crypt_cfg`, `struct ufs_mtk_clk`, `struct ufs_mtk_hw_ver`, `struct ufs_mtk_mcq_intr_info`, and `struct ufs_mtk_host`.

## Control flow and state
No executable flow. The header defines all state tracked by the MediaTek C driver: PHY/regulator/reset handles, clock scaling state, hardware version, capability bits, refclk delays, IP version, MCQ IRQs, and optional PHY device PM handle.

## Dependencies and integration points
Included by `ufs-mediatek.c` and coupled to MediaTek UFSHCI register layout, UFSHCD MCQ support, Linux PHY/regulator/reset/clock types, and firmware operations declared in `ufs-mediatek-sip.h`.

## Risks and test signals
Risks are stale IP version comparisons, bit definitions that gate critical power behavior, and fixed `UFSHCD_MAX_Q_NR` assumptions. Test signals are compile coverage with MCQ and clock scaling enabled, register dumps matching documented offsets, and runtime behavior differences across legacy and newer IP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.h -->
