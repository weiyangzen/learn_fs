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
