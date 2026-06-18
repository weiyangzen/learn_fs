# Research Group subset-b-000653

Grouped research for OMAP2+ ARM machine support files in the Ceph client kernel source snapshot. These files cover TI OMAP/DM81xx hwmod descriptors, OPP and voltage data, PMIC voltage conversion, suspend and cpuidle setup, legacy platform-data quirks, and powerdomain framework/data tables. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_81xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_81xx_data.c

## Purpose
`omap_hwmod_81xx_data.c` describes DM814x/DM816x hardware modules and OCP interconnect links for the legacy OMAP hwmod layer. It maps MPU, L3/L4 buses, UART, watchdog, I2C, ELM, GPIO, GPMC, USB OTG, timers, EMAC/MDIO, SATA, MMC, McSPI, mailbox, and spinbox modules to clockdomains, main clocks, PRCM clock-control offsets, sysconfig layouts, and reset hooks.

## Important APIs, Types, and Functions
The main data types are `struct omap_hwmod`, `struct omap_hwmod_class`, `struct omap_hwmod_class_sysconfig`, `struct omap_hwmod_ocp_if`, `struct omap_hwmod_opt_clk`, and `struct omap_hsmmc_dev_attr`. Entry points are `dm814x_hwmod_init()` and `dm816x_hwmod_init()`, both calling `omap_hwmod_init()` and `omap_hwmod_register_links()`. Important arrays are `dm814x_hwmod_ocp_ifs[]` and `dm816x_hwmod_ocp_ifs[]`.

## Control Flow
Board/SoC init selects the DM814x or DM816x init function. That function initializes hwmod core state, then registers the static OCP link array. Registration pulls in both endpoint hwmods, their class sysconfig metadata, PRCM offsets, module modes, and optional clocks. The hwmod layer later uses this metadata for reset, enable, idle, shutdown, and device instantiation paths.

## State and Persistence Behavior
The file contains static boot-time descriptors, not runtime persistence. Runtime state is held by the hwmod framework, clock framework, PRCM registers, and devices created from DT or auxdata. The descriptor flags matter because they influence whether modules start active, can be idled, have reset status, or skip idlest checks.

## Dependencies and Integration Points
It depends on `omap_hwmod_common_data.h`, `cm81xx.h`, `ti81xx.h`, `wd_timer.h`, and MMC platform data. It integrates with PRCM clockctrl registers, clockdomains such as `alwon_l3s_clkdm`, `default_l3_slow_clkdm`, and `alwon_ethernet_clkdm`, and with drivers consuming hwmod names like `uart1`, `gpio1`, `mmc1`, `davinci_mdio`, and `usb_otg_hs`.

## Risks
The biggest risk is incorrect hardware metadata: a wrong `clkctrl_offs`, `main_clk`, clockdomain, sysconfig offset, reset delay, or shared clock-control assumption can hang boot, break probe, prevent idle, or corrupt wakeup behavior. DM81xx coverage is explicitly incomplete and not generated from the hardware database, so edits require TRM checks and board testing.

## Test Signals
Build with TI81xx/DM814x/DM816x configs and boot on affected boards. Watch for successful registration/probe of UART, MMC, GPIO, GPMC, MDIO/EMAC, SATA, USB, and timers, clean hwmod reset logs, no idlest timeout warnings, and correct suspend/idle behavior. Targeted validation includes enabling/disabling each registered module and checking PRCM clockctrl transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_81xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.c

## Purpose
`omap_hwmod_common_data.c` provides shared hwmod sysconfig bitfield descriptions and a few common device attributes used by multiple OMAP SoC hwmod data files. It centralizes how different IP generations encode idle, standby, wakeup, reset, autoidle, and DMA-disable bits in SYSCONFIG-style registers.

## Important APIs, Types, and Functions
The exported data objects are `omap_hwmod_sysc_type1`, `omap_hwmod_sysc_type2`, `omap_hwmod_sysc_type3`, `omap2_3_dss_dispc_dev_attr`, `omap34xx_sr_sysc_fields`, `omap36xx_sr_sysc_fields`, `omap3_sham_sysc_fields`, `omap3xxx_aes_sysc_fields`, `omap_hwmod_sysc_type_mcasp`, and `omap_hwmod_sysc_type_usb_host_fs`. They are `struct sysc_regbits` or small hwmod device-attribute structures.

## Control Flow
There is no imperative control flow. Other hwmod descriptor files reference these objects through `.sysc_fields` and device attribute pointers. At runtime the hwmod framework reads those offsets while composing register masks and values for reset, idle mode, standby mode, and wakeup configuration.

## State and Persistence Behavior
All state is static descriptor state compiled into the kernel. Persistent effects occur only indirectly when hwmod operations write hardware sysconfig registers based on these shared field maps.

## Dependencies and Integration Points
The file depends on `omap_hwmod.h`, `omap_hwmod_common_data.h`, and `linux/platform_data/ti-sysc.h`. It supports legacy hwmod users and also aligns with the newer `ti-sysc` platform data path in `pdata-quirks.c`.

## Risks
Incorrect bit shifts are high impact because they affect many modules, not one device. A wrong field can disable wakeups, fail resets, select unsupported idle modes, or make crypto/display/SmartReflex/McASP/USB host modules misbehave across several SoCs.

## Test Signals
Compile all OMAP hwmod users. Runtime signals include successful reset/idle cycles for type1, type2, type3, SmartReflex, SHAM, AES, McASP, and USB host FS blocks. Suspended systems should still wake from modules with wakeup-capable sysconfig fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.h

## Purpose
`omap_hwmod_common_data.h` declares shared OMAP2xxx hwmod objects, OCP interface descriptors, hwmod classes, and common display attributes for use by SoC-specific hwmod data files. It is a cross-file contract for older OMAP hwmod tables.

## Important APIs, Types, and Functions
The header declares common `struct omap_hwmod` instances for L3/L4 interconnect, MPU, timers, watchdog, UARTs, DSS blocks, GPIOs, McSPI, GPMC, RNG, SHAM, and AES. It also declares `struct omap_hwmod_ocp_if` links, classes such as `l3_hwmod_class`, `omap2_uart_class`, `omap2_dss_hwmod_class`, and `omap2xxx_gpio_hwmod_class`, plus `omap2_3_dss_dispc_dev_attr`.

## Control Flow
There is no runtime control flow in the header. Its declarations let per-SoC C files compose link arrays and reuse class descriptors. The eventual control flow happens when init code calls `omap_hwmod_register_links()` with arrays containing these declared objects.

## State and Persistence Behavior
The header owns no state. It binds compilation units to shared statically initialized descriptors whose runtime effects are PRCM and sysconfig register programming by the hwmod layer.

## Dependencies and Integration Points
It includes `omap_hwmod.h`, `common.h`, and `display.h`. Integration points are all OMAP2xxx hwmod files that need common bus, display, timer, serial, GPIO, crypto, and GPMC definitions.

## Risks
Changing declarations without matching definitions breaks builds. Renaming or removing shared hwmods can silently destabilize SoC link arrays or DT auxdata paths if only one platform is tested.

## Test Signals
Compile all OMAP2xxx/3xxx configurations that include hwmod support. Useful signals are no unresolved symbols, correct device registration for common modules, and successful display, timer, UART, GPIO, crypto, and GPMC probe on OMAP2-family boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_ipblock_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_ipblock_data.c

## Purpose
`omap_hwmod_common_ipblock_data.c` defines common class descriptors for OMAP display subsystem IP blocks shared across OMAP2+ hwmod data: DSS core and RFBI.

## Important APIs, Types, and Functions
The file defines `omap2_dss_sysc`, `omap2_dss_hwmod_class`, `omap2_rfbi_sysc`, and `omap2_rfbi_hwmod_class`. The DSS class includes `.reset = omap_dss_reset`; both classes encode sysconfig offsets, reset status support, autoidle, sidle modes, and type1 sysconfig fields.

## Control Flow
No local control flow exists. SoC-specific hwmod tables attach these classes to DSS and RFBI hwmods. During hwmod reset/idle sequencing, the class metadata directs register access and optional DSS reset handling.

## State and Persistence Behavior
The data is static. Runtime persistence is limited to hardware state written through hwmod operations: DSS reset state, sysconfig autoidle, and idle mode settings.

## Dependencies and Integration Points
The file depends on `omap_hwmod.h` and `omap_hwmod_common_data.h`, especially `omap_hwmod_sysc_type1`. It integrates with DSS display drivers and legacy OMAP display init paths that still use hwmod reset and idle handling.

## Risks
Wrong offsets or flags can break display reset, leave DSS clocks active, or prevent RFBI from idling. Because display often participates in suspend/resume, mistakes can appear as blank panels or resume hangs rather than immediate boot failures.

## Test Signals
Build display-enabled OMAP2/3 configs. Boot with DSS/RFBI users, verify display probe, reset completion, idle transitions, suspend/resume, and lack of hwmod sysconfig warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_ipblock_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_opp_data.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_opp_data.h

## Purpose
`omap_opp_data.h` defines OMAP-specific OPP and voltage-data helper contracts used by OMAP3/4 voltage and OPP table files. It documents that these helpers are for SoC-level initialization only, not board files or PM core logic.

## Important APIs, Types, and Functions
The key type is `struct omap_opp_def`, containing `hwmod_name`, `freq`, `u_volt`, and `default_available`. Macros are `OPP_INITIALIZER()` and `VOLT_DATA_DEFINE()`. The header declares voltage arrays for OMAP34xx, OMAP36xx, OMAP443x, and OMAP446x voltage domains.

## Control Flow
There is no executable flow. Data files instantiate voltage arrays and, in older code paths, OPP definitions using these macros. Later PM/voltage initialization registers the voltage data with the voltage layer and OPP framework users.

## State and Persistence Behavior
The header stores no state. Its consumers create static voltage tables that influence runtime voltage scaling, SmartReflex calibration, and OPP availability.

## Dependencies and Integration Points
It includes `omap_hwmod.h` and `voltage.h`. It integrates with `opp3xxx_data.c`, `opp4xxx_data.c`, voltage-domain registration, SmartReflex eFuse handling, and hwmod naming conventions.

## Risks
Frequency/voltage data must match silicon validation and eFuse layout. Bad nominal voltages or eFuse offsets can cause undervoltage, excess power, unstable frequency scaling, or SmartReflex miscalibration.

## Test Signals
Compile OMAP3/4 PM and voltage code. Runtime signals include correct voltage-domain registration, cpufreq/OPP availability, SmartReflex calibration reads, and stable operation at each advertised OPP under load and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_opp_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_phy_internal.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_phy_internal.c

## Purpose
`omap_phy_internal.c` performs an early OMAP4430 USB PHY power-down workaround. The internal MUSB PHY is enabled after reset, and leaving it enabled can block core retention; this file powers it down until the USB driver needs it.

## Important APIs, Types, and Functions
The key function is `omap4430_phy_power_down()`, registered with `omap_early_initcall()`. It uses `cpu_is_omap44xx()`, `ioremap(OMAP443X_SCM_BASE, SZ_1K)`, `writel_relaxed(PHY_PD, ctrl_base + CONTROL_DEV_CONF)`, and `iounmap()`.

## Control Flow
During early OMAP init, the callback exits on non-OMAP44xx systems. On OMAP44xx, it maps the SCM control region, writes the `PHY_PD` bit into `CONTROL_DEV_CONF`, unmaps, and returns. Later USB/MUSB driver code owns re-enabling the PHY when needed.

## State and Persistence Behavior
The persistent state is a hardware control-module bit that powers down the PHY. No software state is stored after the early init call.

## Dependencies and Integration Points
It depends on `soc.h` and `control.h`, and indirectly on OMAP4 MUSB/TWL6030 USB integration. It affects PM core retention and USB driver bring-up ordering.

## Risks
Wrong SoC detection or register address can disable unrelated control bits. Removing the early power-down can cause core retention failures, while failing to let USB later re-enable the PHY breaks MUSB operation.

## Test Signals
Boot OMAP4430 with PM enabled and verify core retention is reachable before USB use. Then load/use MUSB and confirm USB still enumerates. Check for control-module ioremap failures and no suspend/resume regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_phy_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_twl.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_twl.c

## Purpose
`omap_twl.c` registers TWL4030/TWL6030 PMIC voltage-control data with OMAP voltage domains. It supplies voltage selector conversion functions, voltage-processor timing parameters, I2C register addresses, and OMAP3/4 PMIC wiring assumptions.

## Important APIs, Types, and Functions
Important functions are `twl4030_vsel_to_uv()`, `twl4030_uv_to_vsel()`, `twl6030_vsel_to_uv()`, `twl6030_uv_to_vsel()`, `omap3_twl_init()`, and `omap4_twl_init()`. Data objects include `omap3_mpu_pmic`, `omap3_core_pmic`, `omap4_mpu_pmic`, `omap4_iva_pmic`, and `omap4_core_pmic`.

## Control Flow
Common PM late init calls `omap3_twl_init()` and `omap4_twl_init()`. OMAP3 registers PMIC data for `mpu_iva` and `core`; OMAP4 registers `mpu`, `iva`, and `core` unless a Motorola CPCAP node is present. TWL6030 conversion lazily reads `REG_SMPS_OFFSET` via TWL I2C and caches the offset.

## State and Persistence Behavior
Static PMIC descriptor data persists for the voltage layer. Mutable file-local state is `is_offset_valid` and `smps_offset`, caching the TWL6030 eFuse offset. Hardware persistence is PMIC voltage register programming through the voltage processor.

## Dependencies and Integration Points
It depends on `linux/mfd/twl.h`, `soc.h`, `voltage.h`, and `pm.h`. It integrates with voltage-domain lookup, `omap_voltage_register_pmic()`, OMAP VC/VP I2C signaling, TWL MFD I2C access, SmartReflex, and OPP voltage scaling.

## Risks
Voltage conversion errors are high risk: they can underpower or overvolt MPU/core/IVA rails. TWL6030 has special >1.3V handling and a hardcoded 1.35V selector; unsupported voltages intentionally log errors and clamp. CPCAP detection must prevent conflicting PMIC registration on Motorola boards.

## Test Signals
Boot OMAP3/TWL4030 and OMAP4/TWL6030 boards, verify PMIC registration for expected voltage domains, exercise cpufreq/OPP voltage changes, validate SmartReflex/VC transactions, and check stable suspend/resume. Confirm CPCAP boards skip TWL OMAP4 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_twl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2420_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2420_data.c

## Purpose
`opp2420_data.c` provides deprecated OMAP2420 PRCM rate tables for legacy clock code. Each table row describes a validated combination of crystal rate, DPLL rate, MPU rate, clock divider register values, SDRC refresh setting, and availability flags.

## Important APIs, Types, and Functions
The exported data is `const struct prcm_config omap2420_rate_table[]`. It uses macros from `opp2xxx.h`, SDRC refresh constants from `sdrc.h`, and `RATE_IN_242X` from clock code.

## Control Flow
No function executes locally. OMAP2 clock initialization scans the sorted table from fastest to slowest and chooses an applicable PRCM set based on SoC, oscillator, and supported flags. Boot-bypass rows provide low-rate fallback.

## State and Persistence Behavior
The file holds immutable clock configuration data. Runtime state is external, notably `rate_table`, `curr_prcm_set`, PRCM registers, and SDRC refresh timing programmed by clock code.

## Dependencies and Integration Points
It depends on `opp2xxx.h`, `sdrc.h`, and `clock.h`. It integrates with OMAP2420 clock rate selection, SDRAM controller refresh programming, and platform support for H4/Nokia-era boards.

## Risks
The format is deprecated and missing voltage data and 19.2 MHz sets. A wrong divider or SDRC refresh value can cause immediate instability, memory corruption, or failed frequency changes. Table order matters because fastest entries are preferred.

## Test Signals
Build OMAP2420 support and boot with 12/13 MHz oscillators. Verify selected MPU/DPLL rates, SDRC refresh values, and stable operation under clock changes if enabled. Look for boot regressions on N800/N810-class configurations due to missing 19.2 MHz handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2420_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2430_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2430_data.c

## Purpose
`opp2430_data.c` provides deprecated OMAP2430 PRCM rate tables for the old OMAP2xxx clock path. It captures ratio configurations for 2430, including differences from 2420 such as no phase synchronizers and a different IVA/modem domain layout.

## Important APIs, Types, and Functions
The exported object is `const struct prcm_config omap2430_rate_table[]`. Rows use `R1`, `R2`, `M4`, `M5A`, `M5B`, and boot-bypass macros from `opp2xxx.h`, plus SDRC refresh constants and `RATE_IN_243X`.

## Control Flow
The clock layer selects an entry based on oscillator and desired/available rate, assuming the table is sorted fastest to slowest. Rows include fast and slow variants and bypass fallbacks.

## State and Persistence Behavior
Only immutable configuration data lives here. Runtime state exists in PRCM register programming, SDRC settings, and the selected current PRCM set tracked by clock code.

## Dependencies and Integration Points
It depends on `opp2xxx.h`, `sdrc.h`, and `clock.h`. It integrates with OMAP2430 clock init and any platform code relying on old-style OPP/rate selection.

## Risks
The table lacks voltage data and 19.2 MHz sys_clk sets. Incorrect ratios can affect MPU, DSP/IVA, GFX, L3/L4, USB, modem, and SDRC timing. Adding rows without preserving sort order can select an unintended slower or unstable operating point.

## Test Signals
Build and boot OMAP2430 targets with supported oscillators. Confirm MPU/DPLL rates, modem divider programming, SDRC refresh timing, and low-power bypass behavior. Stress memory and peripherals after rate selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2430_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2xxx.h

## Purpose
`opp2xxx.h` defines the deprecated OMAP2xxx PRCM configuration structure and the bitfield macros used by OMAP2420/2430 old-style OPP/rate tables. It is effectively a register-programming vocabulary for clock ratios, DPLL multipliers/dividers, and standard speed constants.

## Important APIs, Types, and Functions
The key type is `struct prcm_config`, with oscillator, DPLL, MPU speed, PRCM clock selector values, SDRC refresh base, and flags. Important declarations are `omap2420_rate_table[]`, conditional `omap2430_rate_table[]`, `rate_table`, and `curr_prcm_set`. Macros cover 2420 and 2430 ratio sets, boot-bypass modes, DPLL settings for 12/13/19.2 MHz references, PLL x1/x2 modes, and speed constants.

## Control Flow
The header contains no executable flow. Clock code consumes its structures/macros to select and program PRCM register sets from the SoC-specific tables.

## State and Persistence Behavior
No state is stored in the header. It declares external clock-selection state and defines constants that ultimately persist as hardware PRCM and SDRC register values.

## Dependencies and Integration Points
It integrates directly with `opp2420_data.c`, `opp2430_data.c`, and OMAP2xxx clock code. It also ties old OPP naming to PRCM hardware register layouts.

## Risks
This header is low-level and deprecated; edits can affect every OMAP2xxx rate table. Macro mistakes are hard to diagnose because symptoms can be unstable clocks, memory refresh failures, or peripheral timing issues.

## Test Signals
Build OMAP2420 and OMAP2430 configs. Validate all table rows that use changed macros by checking computed PRCM values, selected MPU/DPLL rates, and stable boot/peripheral operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp3xxx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp3xxx_data.c

## Purpose
`opp3xxx_data.c` defines OMAP34xx and OMAP36xx voltage data tables for the voltage layer and SmartReflex calibration. It maps nominal voltages to control-module eFuse offsets and SmartReflex error parameters.

## Important APIs, Types, and Functions
The exported arrays are `omap34xx_vddmpu_volt_data[]`, `omap34xx_vddcore_volt_data[]`, `omap36xx_vddmpu_volt_data[]`, and `omap36xx_vddcore_volt_data[]`. They are built with `VOLT_DATA_DEFINE()` and include sentinel zero rows.

## Control Flow
There are no local functions. Voltage-domain initialization consumes these arrays after PMIC registration and SoC identification, using nominal voltage entries and eFuse offsets to configure voltage scaling and SmartReflex.

## State and Persistence Behavior
The file contains immutable voltage descriptors. Runtime effects include voltage-domain state, SmartReflex calibration data, and PMIC register programming.

## Dependencies and Integration Points
It depends on `soc.h`, `control.h`, `omap_opp_data.h`, and `pm.h`. It integrates with OMAP3 voltage domains `mpu_iva` and `core`, TWL4030 PMIC support, SmartReflex, and OPP/cpufreq consumers.

## Risks
Wrong voltage values or eFuse offsets can destabilize OMAP3 silicon or break adaptive voltage scaling. OMAP3630 high OPP entries are especially sensitive because they run near upper voltage limits.

## Test Signals
Boot OMAP34xx/36xx boards, verify voltage table registration, eFuse reads, SmartReflex initialization, and stable operation at each CPU/CORE OPP. Run suspend/resume and CPU load tests while monitoring voltage transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp4xxx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp4xxx_data.c

## Purpose
`opp4xxx_data.c` defines OMAP443x and OMAP446x voltage data for MPU, IVA, and CORE domains. It supplies nominal voltages, eFuse offsets, and SmartReflex/voltage-processor error parameters for OMAP4 voltage scaling.

## Important APIs, Types, and Functions
The exported arrays are `omap443x_vdd_mpu_volt_data[]`, `omap443x_vdd_iva_volt_data[]`, `omap443x_vdd_core_volt_data[]`, `omap446x_vdd_mpu_volt_data[]`, `omap446x_vdd_iva_volt_data[]`, and `omap446x_vdd_core_volt_data[]`, all terminated by zero rows.

## Control Flow
No functions execute in this file. Late PM/voltage initialization selects the correct arrays based on OMAP4 revision and registers them with the voltage framework after PMIC data has been attached.

## State and Persistence Behavior
It stores static voltage-calibration data only. Runtime persistence is in voltage domain structures, eFuse-derived calibration, and PMIC/VC/VP programmed state.

## Dependencies and Integration Points
It depends on `soc.h`, `control.h`, `omap_opp_data.h`, and `pm.h`. It integrates with TWL6030 or CPCAP/FAN/MAX8952 PMIC support, SmartReflex, OMAP4 OPP/cpufreq, and the MPU/IVA/CORE voltage domains.

## Risks
OMAP4430 and OMAP4460 tables differ; using the wrong voltages or eFuse offsets can cause unstable high OPPs or excess power. CORE over-voltage entries must remain aligned with silicon requirements.

## Test Signals
Boot OMAP443x/446x boards with their PMICs, verify voltage-domain table selection and eFuse reads, exercise OPP transitions, and run suspend/resume plus CPU/IVA load tests at turbo/nitro-class operating points where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp4xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-quirks.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-quirks.c

## Purpose
`pdata-quirks.c` bridges Devicetree boot with legacy OMAP platform data and board-specific quirks. It supplies auxdata, clockdomain hooks, legacy GPIO setup, MMC names, IOMMU callbacks, SmartReflex data, McBSP data, PRM/sysc platform data, and board initialization callbacks that drivers still require.

## Important APIs, Types, and Functions
Key functions include `pdata_quirks_init()`, `pdata_quirks_init_clocks()`, `pdata_quirks_check()`, `omap_pcs_legacy_init()`, `ti_sysc_clkdm_init()`, `ti_sysc_clkdm_deny_idle()`, `ti_sysc_clkdm_allow_idle()`, and hwmod-backed `ti_sysc_enable_module()`, `ti_sysc_idle_module()`, and `ti_sysc_shutdown_module()`. Important data includes `omap_auxdata_lookup[]`, `auxdata_quirks[]`, `pdata_quirks[]`, `ti_sysc_pdata`, `ti_prm_pdata`, `pcs_pdata`, `mmc_pdata[]`, and `omap_sr_pdata[]`.

## Control Flow
Early DT platform init calls `pdata_quirks_init()`. It initializes SDRC for OMAP2420/OMAP3, optional McBSP pdata, runs auxdata quirks based on root compatible strings, populates PRCM/PRM nodes first, then calls `of_platform_populate()` for the full tree with auxdata. Finally it runs board-specific pdata quirks.

## State and Persistence Behavior
The file mutates platform data structures before device creation. It also writes control-module registers for MMC clock routing, pbias voltage, AM35xx EMAC reset/interrupt clearing, and may export GPIO descriptors for legacy board devices. These effects persist for the boot lifetime.

## Dependencies and Integration Points
It depends on OF platform population, GPIO descriptors, clockdomain/hwmod APIs, OMAP control registers, secure calls, hsmmc, IOMMU, SmartReflex, wkup_m3, McBSP, pinctrl-single, `ti-sysc`, and `ti-prm`. It is an integration hub for old board support such as N8x0, N900, Pandora, Compulab SBCs, AM3517 EVM, and OMAP3 EVM.

## Risks
This file can mask missing DT bindings by injecting platform data. Wrong compatible matching, auxdata addresses, or GPIO lookup tables can break board boot, device probe names, PM reset sequencing, or wakeups. Some quirks manipulate hardware directly before normal drivers own it.

## Test Signals
Boot affected boards or QEMU-equivalent configs and verify DT population order, named MMC devices, IOMMU reset callbacks, SmartReflex pdata, McBSP audio, USB hub reset GPIOs, AM35xx EMAC, and `ti-sysc` clockdomain idle hooks. Watch for probe-name regressions from auxdata changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-asm-offsets.c

## Purpose
`pm-asm-offsets.c` generates assembly constants for AM33xx/AM43xx low-power SRAM code. It ensures hand-written assembly uses correct offsets into C structures shared with PM firmware support.

## Important APIs, Types, and Functions
The only function is `main()`, used by the kernel build offsets generator. It calls `ti_emif_asm_offsets()` and emits `DEFINE()` constants for fields in `struct am33xx_pm_sram_data` and `struct am33xx_pm_ro_sram_data`, plus structure sizes and a `BLANK()`.

## Control Flow
At build time, kbuild compiles/runs this offsets program to produce assembler include definitions. The generated constants are then consumed by AMx3 PM assembly/SRAM routines.

## State and Persistence Behavior
No runtime state exists. The persistent artifact is a generated header/assembly-offset output used during the same build.

## Dependencies and Integration Points
It depends on `linux/kbuild.h`, `linux/platform_data/pm33xx.h`, and `linux/ti-emif-sram.h`. It integrates with AM33xx/AM43xx suspend assembly and EMIF SRAM code.

## Risks
Missing or wrong offsets cause suspend assembly to read/write the wrong SRAM data fields, which can corrupt resume state, WFI flags, RTC base pointers, or L2 cache settings.

## Test Signals
Build AM33xx/AM43xx PM code and inspect generated offsets after structure changes. Runtime validation is successful standby/deepsleep suspend/resume with correct WFI flags, EMIF handling, RTC wake, and cache restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-debug.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-debug.c

## Purpose
`pm-debug.c` exposes debugfs instrumentation for OMAP power management. It reports powerdomain state counters, time spent in states, clockdomain usecounts, per-powerdomain suspend targets, and global off-mode control.

## Important APIs, Types, and Functions
Key functions are `pm_dbg_update_time()`, `pm_dbg_counters_show()`, `pm_dbg_timers_show()`, `pwrdm_suspend_get()`, `pwrdm_suspend_set()`, `option_get()`, `option_set()`, and `pm_dbg_init()`. It uses debugfs show helpers, `pwrdm_for_each()`, `clkdm_for_each()`, `omap3_pm_get_suspend_state()`, and `omap3_pm_set_suspend_state()`.

## Control Flow
When `CONFIG_DEBUG_FS` is enabled, `omap_arch_initcall(pm_dbg_init)` creates `/sys/kernel/debug/pm_debug`. It installs `count`, `time`, `enable_off_mode`, and per-powerdomain `suspend` files. Powerdomain transitions call `pm_dbg_update_time()` to accumulate timers after init completes.

## State and Persistence Behavior
Debug state lives in `pm_dbg_init_done`, `enable_off_mode`, and per-powerdomain counters/timers embedded in `struct powerdomain`. Writing `enable_off_mode` can immediately reprogram OMAP3 suspend targets.

## Dependencies and Integration Points
It depends on debugfs, seq_file, scheduler clock, clockdomain and powerdomain frameworks, OMAP SoC detection, and OMAP3 PM suspend-state APIs.

## Risks
Debugfs writes can change suspend behavior on live systems. Timer accounting assumes valid previous state indexes. Calling `pwrdm_state_switch()` from debug display can perturb transition bookkeeping.

## Test Signals
With `CONFIG_PM_DEBUG` and `CONFIG_DEBUG_FS`, mount debugfs and read `pm_debug/count` and `pm_debug/time` before and after idle/suspend. Change OMAP3 per-domain `suspend` and `enable_off_mode` values and verify expected PM behavior without state mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.c

## Purpose
`pm.c` contains common OMAP2+ PM glue shared by SoC-specific PM implementations. It registers platform suspend operations, stores global off-mode policy, exposes oscillator latency data, idles clockdomains, and runs late PM initialization.

## Important APIs, Types, and Functions
Important symbols are global `enable_off_mode`, `omap_pm_soc_init`, `omap_pm_clkdms_setup()`, `omap_pm_get_oscillator()`, `omap_common_suspend_init()`, `omap_pm_nop_init()`, and late init `omap2_common_pm_late_init()`. Suspend callbacks include `omap_pm_begin()`, `omap_pm_enter()`, `omap_pm_end()`, and `omap_pm_wake()`.

## Control Flow
SoC PM code calls `omap_common_suspend_init()` with its suspend function. The generic suspend ops then route `PM_SUSPEND_MEM` into that SoC function, while begin/end toggle CPU idle polling and OMAP3 PRCM IRQ preparation/completion. Late init registers PMIC data, initializes voltage, SmartReflex, calls `omap_pm_soc_init()`, and enables clock autoidle.

## State and Persistence Behavior
Global state includes `enable_off_mode`, the SoC suspend function pointer, optional oscillator latency data, and `omap_pm_soc_init`. Hardware state changes happen through voltage initialization, SmartReflex device init, clockdomain idle permissions, and clock autoidle.

## Dependencies and Integration Points
It depends on suspend core, OPP/voltage code, clockdomain/powerdomain frameworks, OMAP PRCM IRQ helpers, TWL/CPCAP PMIC init, SmartReflex, and SoC-specific PM modules such as `pm34xx.c` and `pm44xx.c`.

## Risks
Ordering is important: PMIC and voltage init must precede SoC PM setup. A missing suspend function causes suspend to return `-ENOENT`; wrong begin/wake handling can lose OMAP3 PRCM wake interrupts.

## Test Signals
Boot OMAP3/4/AMx3 with PM enabled, confirm late init logs no SoC PM failure, suspend-to-RAM enters the SoC path, clock autoidle is enabled, and PRCM wake handling works on OMAP3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.h

## Purpose
`pm.h` is the central private PM header for mach-omap2. It declares OMAP idle/suspend entry points, shared globals, SRAM routines, errata flags, PMIC init hooks, oscillator latency access, and common suspend registration.

## Important APIs, Types, and Functions
Key declarations include `omap3_idle_init()`, `omap4_idle_init()`, `omap_sram_idle()`, `omap_pm_clkdms_setup()`, `omap3_pm_get_suspend_state()`, `omap3_pm_set_suspend_state()`, `enable_off_mode`, OMAP24xx/34xx suspend assembly hooks, AM33xx SRAM address structures, `pm34xx_errata`, `pm44xx_errata`, `omap_devinit_smartreflex()`, `omap3_twl_init()`, `omap4_twl_init()`, `omap4_cpcap_init()`, `omap_pm_get_oscillator()`, and `omap_common_suspend_init()`.

## Control Flow
The header controls build-time availability with configuration stubs. Callers can invoke PMIC or SmartReflex initialization without scattering `#ifdef`s; disabled features return `-EINVAL` or no-op.

## State and Persistence Behavior
It owns no definitions except macros and stubs, but it exposes global PM state and errata masks used to decide suspend paths and workarounds.

## Dependencies and Integration Points
It includes `powerdomain.h` and is used by `pm.c`, `pm34xx.c`, `pm44xx.c`, `pm33xx-core.c`, PMIC files, powerdomain code, and assembly support.

## Risks
Header stubs define behavior when subsystems are disabled; changing return values can alter init error handling. Errata macro changes affect low-power safety paths across SoCs.

## Test Signals
Build with combinations of `CONFIG_PM`, `CONFIG_SUSPEND`, `CONFIG_CPU_IDLE`, `CONFIG_TWL4030_CORE`, `CONFIG_MFD_CPCAP`, `CONFIG_POWER_AVS_OMAP`, and SoC options. Verify no missing symbols and expected PM feature enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm33xx-core.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm33xx-core.c

## Purpose
`pm33xx-core.c` provides AM33xx/AM43xx architecture PM callbacks, cpuidle glue, and platform data for the `pm33xx` driver. It coordinates powerdomains, clockdomains, SCU mode, secure monitor calls, context save/restore, SRAM address lookup, and initial suspend blocking until firmware support is ready.

## Important APIs, Types, and Functions
Important functions include `amx3_common_pm_init()`, `am33xx_suspend_init()`, `am43xx_suspend_init()`, `am33xx_suspend()`, `am43xx_suspend()`, `am33xx_cpu_suspend()`, `am43xx_cpu_suspend()`, `amx3_idle_init()`, and `amx3_idle_enter()`. Key data types are `struct am33xx_pm_platform_data` and `struct amx3_idle_state`.

## Control Flow
Common PM init registers a `pm33xx` platform device carrying SoC-specific ops and installs blocked suspend ops. The driver later calls init ops with an SRAM idle function. Suspend powers down GFX, enters CPU suspend, performs AM33xx GFX clockdomain wake/sleep workaround, or for AM43xx switches SCU modes and calls secure monitor suspend/resume on HS devices. Cpuidle parses `cpu-idle-states` phandles and maps `ti,idle-wkup-m3` to WFI flags.

## State and Persistence Behavior
Static state tracks powerdomain and clockdomain pointers, SCU mapping, `idle_fn`, and allocated `idle_states`. Hardware state includes GFX/CEFUSE domain targets, SCU power mode, INTC context, and AM43xx secure-side suspend state.

## Dependencies and Integration Points
It depends on cpuidle, platform suspend, wkup_m3 IPC, RTC, OMAP secure calls/SMCCC, clockdomain/powerdomain frameworks, SRAM support, AM33xx/AM43xx PRCM, and `pm33xx` platform data consumers.

## Risks
Suspend requires firmware and wkup_m3 IPC; premature suspend is blocked. Wrong SCU or secure-call handling can hang AM43xx resume. AM33xx GFX_L4LS workaround is required to avoid clockdomain transition stalls.

## Test Signals
Boot AM335x/AM437x, confirm `pm33xx` platform device registration and blocked suspend warning before firmware. With firmware, test standby/deepsleep, RTC wake, wkup_m3 idle states, GFX domain transition logs, INTC context restore, and HS/OP-TEE secure suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm33xx-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm34xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm34xx.c

## Purpose
`pm34xx.c` implements OMAP3 power management: idle entry, suspend-to-RAM, powerdomain target setup, PRCM wake IRQ handling, context save/restore, errata handling, secure RAM save, and OMAP3-specific PM initialization.

## Important APIs, Types, and Functions
Key exported symbols are `pm34xx_errata`, `omap_sram_idle()`, `omap3_pm_off_mode_enable()`, `omap3_pm_get_suspend_state()`, `omap3_pm_set_suspend_state()`, `omap_push_sram_idle()`, and `omap3_pm_init()`. Internal functions include `omap3_core_save_context()`, `omap3_core_restore_context()`, PRCM IRQ handlers, `omap34xx_save_context()`, `omap3_pm_suspend()`, `pwrdms_setup()`, and `pm_errata_configure()`.

## Control Flow
`omap3_pm_init()` configures errata, PRCM registers, wake/io IRQs, PMIC off-mode policy, powerdomain target list, clockdomain idle setup, powerdomain lookups, generic suspend registration, idle hook, wake dependencies, secure RAM save, and scratchpad save. Idle reads target states, prepares transitions, saves core/SDRC/INTC/control context when needed, configures PMIC signaling, enters SRAM WFI or CPU suspend, restores context, and updates powerdomain transition state.

## State and Persistence Behavior
State includes `pwrst_list`, `mpu_pwrdm`, `neon_pwrdm`, `core_pwrdm`, `per_pwrdm`, `omap3_do_wfi_sram`, `pm34xx_errata`, secure RAM storage, and saved suspend targets. Hardware state spans PRCM IRQ status, powerdomain targets, INTC/control/CM/SDRC/SRAM context, PMIC signaling, and wake dependencies.

## Dependencies and Integration Points
It depends on CPU PM, suspend, cpuidle, clockdomain/powerdomain, PRM/CM/control/SDRC, SRAM function copy, secure services, VC PMIC signaling, OMAP interrupt controller, and generic `pm.c` suspend registration.

## Risks
OMAP3 off-mode is sensitive to silicon errata i582/i583/i608, secure device ROM behavior, and PMIC DT nodes. Failing context save/restore or PRCM IRQ ordering can hang resume or lose wakeups. Debugfs can alter target states at runtime.

## Test Signals
Boot OMAP3430/3630/AM35x variants, verify PRCM IRQ request success, idle and suspend target states, off-mode enable detection from TWL power nodes, secure RAM save on HS/EMU devices, wake from IO and PRCM events, and no context loss after repeated suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm34xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm44xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm44xx.c

## Purpose
`pm44xx.c` implements OMAP4+ PM initialization and suspend setup for OMAP4, OMAP5, and DRA7-class SoCs. It programs powerdomain targets, logic retention targets, static clockdomain wake dependencies, MPUSS initialization, CPU idle hook, and errata flags.

## Important APIs, Types, and Functions
Key exported functions are `omap4_pm_init_early()` and `omap4_pm_init()`, with global `pm44xx_errata`. Internal functions include `omap4_pm_suspend()`, `pwrdms_setup()`, `omap_default_idle()`, and `omap4plus_init_static_deps()`. Important data includes `struct power_state`, `struct static_dep_map`, `omap4_static_dep_map[]`, and `omap5_dra7_static_dep_map[]`.

## Control Flow
Early init sets errata bits for OMAP446x GICD ROM issue and disables CPU OSWR on OMAP5/DRA7. Main init rejects OMAP4430 ES1.0, creates per-powerdomain target state records, adds static wake dependencies, initializes MPUSS, allows clockdomain idle, registers generic suspend, and sets `arm_pm_idle`. Suspend saves current targets, programs requested targets, calls `omap4_enter_lowpower()` for the active CPU, checks previous states, then restores targets.

## State and Persistence Behavior
State includes `pm44xx_errata`, `cpu_suspend_state`, and `pwrst_list`. Hardware state includes powerdomain target/logic-retention registers, static clockdomain wake dependencies, MPUSS low-power setup, and CPU idle behavior.

## Dependencies and Integration Points
It depends on OMAP low-power CPU entry, MPUSS init, clockdomain/powerdomain frameworks, generic suspend core, and SoC detection. It integrates with `powerdomains44xx_data.c`, `powerdomains54xx_data.c`, and `powerdomains7xx_data.c`.

## Risks
Incorrect target selection can request unsupported power states; the code uses `pwrdm_get_valid_lp_state()` to avoid hangs. Static dependencies work around hardware issues; removing them can cause lockups or bad 32 kHz timer reads. Bootloader version matters for OMAP4 PM.

## Test Signals
Boot OMAP4/5/DRA7, confirm PM init succeeds, powerdomain setup logs no errors, static dependency creation succeeds, MPUSS init succeeds, idle hook works, and suspend reports domains reaching targets. Test CPU hotplug/suspend interactions on dual-core systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pmic-cpcap.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pmic-cpcap.c

## Purpose
`pmic-cpcap.c` registers PMIC voltage-control data for Motorola OMAP4 CPCAP systems and associated external regulators. It covers CPCAP core/IVA regulators, MAX8952 MPU regulator, and FAN535503/FAN535508 regulators used on non-Droid-Bionic CPCAP boards.

## Important APIs, Types, and Functions
Important functions are `omap_cpcap_vsel_to_uv()`, `omap_cpcap_uv_to_vsel()`, `omap_max8952_vsel_to_uv()`, `omap_max8952_uv_to_vsel()`, `omap_fan535503_vsel_to_uv()`, `omap_fan535508_vsel_to_uv()`, corresponding `uv_to_vsel()` helpers, `omap4_cpcap_init()`, and `cpcap_late_init()`. Data objects are `omap_cpcap_core`, `omap_cpcap_iva`, `omap443x_max8952_mpu`, `omap4_fan_core`, and `omap4_fan_iva`.

## Control Flow
Common late PM init calls `omap4_cpcap_init()`. It returns unless a `motorola,cpcap` node exists, registers MAX8952 for `mpu`, then registers CPCAP core/IVA only on `motorola,droid-bionic` or FAN regulators otherwise. A late initcall configures OMAP4 VC PMIC signaling to retention for CPCAP boards.

## State and Persistence Behavior
All descriptor state is static. Hardware state is voltage-domain PMIC registration and VC/VP signaling configuration. Conversion helpers clamp selector/voltage values into supported ranges.

## Dependencies and Integration Points
It depends on OF compatible detection, `voltage.h`, `pm.h`, `vc.h`, and OMAP4 SoC detection. It integrates with Motorola CPCAP MFD/PMIC DT nodes, OMAP voltage domains, and OPP scaling.

## Risks
Board-specific regulator topology matters. Selecting CPCAP versus FAN core/IVA regulators incorrectly can program the wrong I2C slave/register pair. Voltage clamping hides invalid requests but can still produce unstable OPP behavior if tables and regulators disagree.

## Test Signals
Boot Motorola CPCAP OMAP4 boards, verify PMIC registration for `mpu`, `core`, and `iva`, confirm VC signaling setup, exercise OPP transitions, and compare actual rail voltages where possible. Test both Droid Bionic and non-Bionic CPCAP board compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pmic-cpcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain-common.c

## Purpose
`powerdomain-common.c` provides shared helpers for mapping powerdomain memory-bank indexes to OMAP3/OMAP4 register masks. It abstracts common memory on-state, retention-state, and status bitfields used by arch-specific `pwrdm_ops`.

## Important APIs, Types, and Functions
The exported functions are `omap2_pwrdm_get_mem_bank_onstate_mask()`, `omap2_pwrdm_get_mem_bank_retst_mask()`, and `omap2_pwrdm_get_mem_bank_stst_mask()`. They accept a bank index 0-4 and return register masks such as `OMAP_MEM0_ONSTATE_MASK`, `OMAP_MEM4_RETSTATE_MASK`, or warn on invalid indexes.

## Control Flow
Each helper is a switch over the bank number. Invalid banks trigger `WARN_ON(1)` and return `-EEXIST` cast through `u32`. OMAP powerdomain operation implementations call these helpers while programming or reading memory-bank state fields.

## State and Persistence Behavior
There is no stored state. The returned masks control persistent hardware register reads/writes in callers.

## Dependencies and Integration Points
It depends on PM, CM, and PRM register-bit headers. It integrates with OMAP2/3/4 powerdomain operation backends that implement the generic `pwrdm_ops` interface.

## Risks
Bank-to-mask mapping is global and low-level. Wrong masks can cause the framework to program one memory bank while believing it programmed another, leading to retention/off failures or context loss.

## Test Signals
Build OMAP3/4 PM. Exercise powerdomains with 1-5 memory banks and verify memory on/retention states through debugfs counters, PRM registers, and suspend/resume stability. Invalid bank warnings should never occur in normal operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.c

## Purpose
`powerdomain.c` implements the generic OMAP powerdomain framework. It registers SoC-specific operation callbacks and powerdomain descriptors, tracks state counters, associates clockdomains, validates requested states, programs next power states, manages transition bookkeeping, and saves/restores powerdomain context for AM43xx RTC-DDR suspend.

## Important APIs, Types, and Functions
Public APIs include `pwrdm_register_platform_funcs()`, `pwrdm_register_pwrdms()`, `pwrdm_complete_init()`, `pwrdm_lookup()`, `pwrdm_for_each()`, `pwrdm_add_clkdm()`, `pwrdm_set_next_pwrst()`, read/set helpers for logic and memory states, `pwrdm_enable_hdwr_sar()`, `pwrdm_state_switch_nolock()`, `pwrdm_pre_transition()`, `pwrdm_post_transition()`, `pwrdm_get_valid_lp_state()`, and `omap_set_pwrdm_state()`.

## Control Flow
SoC data files first register `struct pwrdm_ops`, then arrays of `struct powerdomain`, then call complete init. Registration validates names, PRCM partitions, voltage-domain links, initializes locks and counters, reads current state, and appends to `pwrdm_list`. State changes validate support, optionally wake the first associated clockdomain, program next state through arch ops, then restore clockdomain behavior and update counters.

## State and Persistence Behavior
Core state is `pwrdm_list`, `arch_pwrdm`, per-powerdomain locks, current state, state counters, logic/memory off counters, voltage-domain links, clockdomain arrays, and optional context snapshots. Hardware state is all PRM/CM powerdomain state controlled through `arch_pwrdm` callbacks.

## Dependencies and Integration Points
It depends on CPU PM notifiers, tracepoints, clockdomain and voltage frameworks, SoC detection, and the SoC-specific `pwrdm_ops` implementations in PRM/CM code. PM files call pre/post transition hooks and state setters during idle/suspend.

## Risks
The framework assumes the first clockdomain can be forced awake for some transitions. Unsupported power states are often degraded rather than hard-failed, which can hide data-table problems. Missing arch callbacks return errors or leave stale state. Context save/restore is only registered for AM43xx when off-mode is enabled.

## Test Signals
Boot each SoC family and verify powerdomain registration, no duplicate names, valid voltage-domain links, and no transition timeouts. Use PM debug counters/tracepoints to confirm target versus achieved states. Suspend/resume should preserve context and not emit state mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.h

## Purpose
`powerdomain.h` defines the OMAP powerdomain data model, power-state constants, feature flags, limits, SoC operation callback interface, and public framework API.

## Important APIs, Types, and Functions
Important constants are `PWRDM_POWER_OFF`, `PWRDM_POWER_RET`, `PWRDM_POWER_INACTIVE`, `PWRDM_POWER_ON`, state bitfields such as `PWRSTS_OFF_RET_ON`, flags such as `PWRDM_HAS_HDWR_SAR`, `PWRDM_HAS_MPU_QUIRK`, and `PWRDM_HAS_LOWPOWERSTATECHANGE`, plus `PWRDM_MAX_MEM_BANKS` and `PWRDM_MAX_CLKDMS`. Key types are `struct powerdomain` and `struct pwrdm_ops`.

## Control Flow
No code executes in the header. It defines contracts used by data files, PRM/CM operation backends, PM code, debugfs code, clockdomain association, and voltage-domain registration.

## State and Persistence Behavior
`struct powerdomain` contains both descriptor data and mutable runtime state: voltage-domain pointer, clockdomain list, list nodes, current state, counters, locks, debug timers, and context shadow. `struct pwrdm_ops` abstracts hardware register access.

## Dependencies and Integration Points
It includes list and spinlock types and is included by almost every OMAP PM/powerdomain file. It integrates with clockdomain and voltage-domain structures by forward declaration.

## Risks
Changing structure layout affects static initializers and debug/context code. Raising/lowering limits for banks or clockdomains impacts data tables. Callback contract changes require updating every SoC backend.

## Test Signals
Build all mach-omap2 PM configs. Runtime signals include successful powerdomain registration, correct debugfs counter/timer behavior, valid memory-bank programming, and no lockdep or transition warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.c

## Purpose
`powerdomains2xxx_3xxx_data.c` defines powerdomain descriptors shared by OMAP2 and OMAP3: the graphics powerdomain and wakeup powerdomain. It captures common PRCM offsets, allowed states, memory-bank behavior, and voltage-domain names.

## Important APIs, Types, and Functions
The exported descriptors are `gfx_omap2_pwrdm` and `wkup_omap2_pwrdm`. `gfx_omap2_pwrdm` supports OFF/RET/ON with one memory bank retained in RET and ON in ON. `wkup_omap2_pwrdm` is always ON.

## Control Flow
There is no local function flow. OMAP2 and OMAP3 SoC-specific init arrays include these descriptors when appropriate; the generic framework registers them and initializes their state.

## State and Persistence Behavior
The descriptors are static but become mutable after registration because `struct powerdomain` includes list nodes, counters, locks, and voltage-domain pointer replacement.

## Dependencies and Integration Points
It depends on `powerdomain.h`, `prcm-common.h`, and `prm.h`. It is declared by `powerdomains2xxx_3xxx_data.h` and consumed by `powerdomains2xxx_data.c` and `powerdomains3xxx_data.c`.

## Risks
The file notes GFX is not present on 3430ES2, so SoC-specific arrays must include it carefully. Shared descriptor mutation means the same object should not be registered twice in one boot path.

## Test Signals
Boot OMAP2/3 variants and verify expected presence/absence of `gfx_pwrdm` and always-on `wkup_pwrdm`. Use PM debugfs to confirm counters and valid state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.h

## Purpose
`powerdomains2xxx_3xxx_data.h` declares the shared OMAP2/3 powerdomain descriptors defined in `powerdomains2xxx_3xxx_data.c`.

## Important APIs, Types, and Functions
It declares `extern struct powerdomain gfx_omap2_pwrdm;` and `extern struct powerdomain wkup_omap2_pwrdm;`.

## Control Flow
There is no control flow. SoC-specific data files include the header and reference the shared descriptors in their init arrays.

## State and Persistence Behavior
The header owns no state but exposes mutable `struct powerdomain` objects to OMAP2/3 registration code.

## Dependencies and Integration Points
It includes `powerdomain.h` and integrates with OMAP2/3 data files that need the shared GFX and WKUP domains.

## Risks
Declaration/definition mismatch breaks builds. Incorrect sharing can register a descriptor on SoCs where the hardware block is absent.

## Test Signals
Compile OMAP2 and OMAP3 powerdomain data. Boot each SoC family and ensure shared domains are registered only on valid variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_3xxx_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_data.c

## Purpose
`powerdomains2xxx_data.c` defines and registers OMAP2420/2430 powerdomain sets. It covers DSP, MPU, CORE, shared WKUP/GFX, and the OMAP2430 modem powerdomain.

## Important APIs, Types, and Functions
Important descriptors are `dsp_pwrdm`, `mpu_24xx_pwrdm`, `core_24xx_pwrdm`, and `mdm_pwrdm`. Init arrays are `powerdomains_omap24xx[]` and `powerdomains_omap2430[]`. Entry points are `omap242x_powerdomains_init()` and `omap243x_powerdomains_init()`.

## Control Flow
Each init function checks CPU type, registers `omap2_pwrdm_operations`, registers common OMAP24xx domains, optionally registers the 2430 modem domain, then calls `pwrdm_complete_init()` to force initial next states to ON.

## State and Persistence Behavior
Static descriptors become runtime framework state after registration. Hardware power targets are initialized to ON by `pwrdm_complete_init()` to avoid context loss in non-PM kernels.

## Dependencies and Integration Points
It depends on SoC detection, shared OMAP2/3 data, PRCM/PRM register offsets, and `omap2_pwrdm_operations`. It integrates with OMAP2 clockdomain and PM paths.

## Risks
OMAP2420 and 2430 have different DSP/modem topology. Registering `mdm_pwrdm` on 2420 or missing it on 2430 would misrepresent hardware. Memory-bank state definitions affect retention/off behavior.

## Test Signals
Boot OMAP2420 and OMAP2430 configs, confirm correct domain list, no PRCM operation failures, and valid transitions for DSP/MPU/CORE/GFX/MDM. PM debugfs should show initial ON state counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains2xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains33xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains33xx_data.c

## Purpose
`powerdomains33xx_data.c` defines AM33xx powerdomain descriptors and registers them with the AM33xx PRM backend. It covers GFX, RTC, WKUP, PER, MPU, and CEFUSE domains with AM33xx-specific register offsets and bit masks.

## Important APIs, Types, and Functions
Descriptors include `gfx_33xx_pwrdm`, `rtc_33xx_pwrdm`, `wkup_33xx_pwrdm`, `per_33xx_pwrdm`, `mpu_33xx_pwrdm`, and `cefuse_33xx_pwrdm`. The init array is `powerdomains_am33xx[]`; entry point is `am33xx_powerdomains_init()`.

## Control Flow
Init registers `am33xx_pwrdm_operations`, registers all AM33xx domains, and completes initialization. Later `pm33xx-core.c` looks up several domains and controls GFX/CEFUSE during suspend setup.

## State and Persistence Behavior
Descriptors contain both generic state capabilities and AM33xx-specific register masks for control/status fields. After registration, mutable runtime state is stored in each descriptor object.

## Dependencies and Integration Points
It depends on `prm33xx.h`, `prm-regbits-33xx.h`, `prcm-common.h`, and AM33xx powerdomain operation callbacks. It integrates with AM33xx PM, cpuidle, and suspend firmware paths.

## Risks
AM33xx uses explicit `pwrstctrl_offs`, `pwrstst_offs`, and masks per memory bank; mask mistakes directly break state programming. PER and MPU have multiple memory banks and low-power state-change flags, increasing risk.

## Test Signals
Boot AM335x, verify all domains register, CEFUSE can be powered off on GP devices, GFX and PER domains transition during suspend, and debugfs counters match expected states after deepsleep/standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains33xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains3xxx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains3xxx_data.c

## Purpose
`powerdomains3xxx_data.c` defines OMAP3, AM35x, and TI81xx powerdomain descriptors and TI81xx-specific powerdomain operations. It selects descriptor sets based on exact silicon revision and registers them with the generic framework.

## Important APIs, Types, and Functions
Important OMAP3 descriptors include `iva2_pwrdm`, `mpu_3xxx_pwrdm`, core variants, `dss_pwrdm`, `sgx_pwrdm`, `cam_pwrdm`, `per_pwrdm`, `emu_pwrdm`, `neon_pwrdm`, `usbhost_pwrdm`, and DPLL pseudo-domains. TI81xx descriptors include ALWON, DEVICE, ACTIVE, DEFAULT, IVHD/GEM/HDVPSS/SGX/ISP domains. Entry point is `omap3xxx_powerdomains_init()`. TI81xx callbacks include set/read power state and wait-transition helpers.

## Control Flow
Init exits unless OMAP34xx or TI81xx. Non-TI81xx registers `omap3_pwrdm_operations`; TI81xx paths register custom `ti81xx_pwrdm_operations`. Revision selection registers AM35x, TI814x, TI816x, or OMAP3430 common plus ES-specific arrays, then calls `pwrdm_complete_init()`.

## State and Persistence Behavior
Static descriptors become mutable runtime powerdomain state. TI81xx callbacks persist hardware power targets in TI81xx PRM registers and poll transition bits with a bailout timeout.

## Dependencies and Integration Points
It depends on SoC/revision detection, shared OMAP2/3 domains, PRM/CM register headers, and OMAP3/TI81xx backend operations. It feeds OMAP3 PM code, hwmod code, and PM debug.

## Risks
Revision gating is critical: OMAP3430 ES3.1+ enables hardware SAR for core/USBTLL while earlier chips avoid broken SAR errata. AM35x domains are mostly ON-only. TI81xx has custom register layout and a special GFX status source. Wrong selection can hang suspend or misread state.

## Test Signals
Boot OMAP3430 ES1/ES2/ES3.1, OMAP3630, AM35x, TI814x, and TI816x where available. Verify correct domain list, SAR flag behavior, TI81xx transition polling, and stable off/retention transitions under OMAP3 PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains43xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains43xx_data.c

## Purpose
`powerdomains43xx_data.c` defines AM43xx powerdomains using the OMAP4-style PRCM backend but disables voltage-domain association through a custom callback. It covers GFX, MPU, RTC, WKUP, TAMPER, CEFUSE, and PER.

## Important APIs, Types, and Functions
Descriptors include `gfx_43xx_pwrdm`, `mpu_43xx_pwrdm`, `rtc_43xx_pwrdm`, `wkup_43xx_pwrdm`, `tamper_43xx_pwrdm`, `cefuse_43xx_pwrdm`, and `per_43xx_pwrdm`. The init array is `powerdomains_am43xx[]`. Entry point is `am43xx_powerdomains_init()`, and `am43xx_check_vcvp()` returns 0 for `pwrdm_has_voltdm`.

## Control Flow
Init patches `omap4_pwrdm_operations.pwrdm_has_voltdm`, registers the OMAP4 operations, registers the AM43xx descriptors, then completes powerdomain init.

## State and Persistence Behavior
Descriptors become mutable runtime framework objects. Hardware state is programmed through OMAP4-style PRCM operations; voltage-domain linking is skipped because AM43xx does not use the same VC/VP association.

## Dependencies and Integration Points
It depends on AM43xx PRCM offsets and `omap4_pwrdm_operations`. It integrates with `pm33xx-core.c`, which maps SCU and controls AM43xx suspend behavior.

## Risks
Mutating global `omap4_pwrdm_operations` is intentional but affects subsequent registration in the same boot; ordering must remain AM43xx-specific. PER and MPU memory-bank arrays must align with AM43xx PRM fields.

## Test Signals
Boot AM437x, verify no voltage-domain lookup errors, all seven domains register, SCU/PM suspend paths work, and GFX/PER/MPU transitions are reflected in PM debug counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains43xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains44xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains44xx_data.c

## Purpose
`powerdomains44xx_data.c` defines OMAP44xx powerdomain descriptors generated from TI hardware databases. It models CORE, GFX, ABE, DSS, TESLA, WKUP, CPU0/CPU1, EMU, MPU, IVAHD, CAM, L3INIT, L4PER, always-on core, and CEFUSE domains.

## Important APIs, Types, and Functions
The main API is `omap44xx_powerdomains_init()`, which registers `omap4_pwrdm_operations` and `powerdomains_omap44xx[]`. Each descriptor declares PRM partition, instance offset, voltage domain, supported states, logic-retention states, memory-bank state capabilities, and low-power-state-change flags where supported.

## Control Flow
OMAP4 SoC init calls `omap44xx_powerdomains_init()`. The generic framework registers all descriptors and initializes their next states to ON. Later `pm44xx.c` programs suspend targets using `pwrdm_get_valid_lp_state()`.

## State and Persistence Behavior
Generated static descriptors become mutable runtime objects. Hardware power state persists in OMAP4 PRM partition registers via `omap4_pwrdm_operations`.

## Dependencies and Integration Points
It depends on OMAP4430 PRM/PRCM register headers and powerdomain framework APIs. It integrates with OMAP4 voltage domains, clockdomains, MPUSS low-power code, and PM suspend setup.

## Risks
Generated data should stay synchronized with hardware databases. Wrong PRCM partition/offset or memory-bank capability can hang suspend or cause data loss. CPU powerdomains are treated specially by `pm44xx.c`.

## Test Signals
Boot OMAP4430/4460/4470 variants, verify domain registration, voltage-domain association, PM init target setup, and suspend/idle transitions for CORE, MPU, CPU, ABE, DSS, GFX, and L4PER domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains44xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains54xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains54xx_data.c

## Purpose
`powerdomains54xx_data.c` defines OMAP54xx powerdomain descriptors for the OMAP4-style framework. It covers CORE, ABE, COREAON, DSS, CPU0/CPU1, EMU, MPU, CUSTEFUSE, DSP, CAM, L3INIT, GPU, WKUPAON, and IVA.

## Important APIs, Types, and Functions
The entry point is `omap54xx_powerdomains_init()`, registering `omap4_pwrdm_operations` and `powerdomains_omap54xx[]`. Descriptors define voltage domains `core`, `mpu`, `wkup`, and `mm`, PRM partitions/instances, supported power states, logic-retention states, memory-bank retention/on states, and low-power-state-change flags.

## Control Flow
SoC powerdomain init registers the descriptor list and completes generic initialization. `pm44xx.c` then treats OMAP5 as an OMAP4+ PM target, including CPU OSWR disable erratum handling and static MPU-to-EMIF dependency.

## State and Persistence Behavior
Static descriptors become runtime powerdomain objects with counters, locks, and voltage-domain pointers. Hardware state is persisted in OMAP54xx PRM registers.

## Dependencies and Integration Points
It depends on OMAP54xx PRM/PRCM/MPU PRCM headers and the generic powerdomain framework. It integrates with OMAP5 PM, clockdomains, voltage domains, and CPU low-power code.

## Risks
Some memory-bank `pwrsts_mem_on` values are retention/off-retention rather than simply ON, so assumptions from OMAP4 data may not apply. Bad generated offsets or state capabilities can break deep idle or context retention.

## Test Signals
Boot OMAP5, verify all listed domains register and PM init succeeds, check MPU/CPU/CORE/DSP/GPU/IVA transitions through debugfs or tracepoints, and run suspend/idle cycles without context-loss warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains54xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains7xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains7xx_data.c

## Purpose
`powerdomains7xx_data.c` defines DRA7xx/DRA72x/DRA74x/DRA76x powerdomain descriptors. It models multimedia, CPU, interconnect, wakeup, DSP, EVE, camera, display, GPU, VPE, efuse, and always-on domains for the OMAP4-style framework.

## Important APIs, Types, and Functions
The entry point is `dra7xx_powerdomains_init()`. Base descriptors are in `powerdomains_dra7xx[]`, with variant-specific `powerdomains_dra76x[]`, `powerdomains_dra74x[]`, and `powerdomains_dra72x[]` selecting customer efuse behavior. Domains include IVA, RTC, IPU, DSS, L4PER, GPU, WKUPAON, CORE, COREAON, CPU0/CPU1, VPE, MPU, L3INIT, EVE1-4, EMU, DSP1/2, and CAM.

## Control Flow
Init registers `omap4_pwrdm_operations`, registers the common DRA7xx domain set, then conditionally registers the appropriate CUSTEFUSE domain based on `soc_is_dra76x()`, `soc_is_dra74x()`, or `soc_is_dra72x()`. It completes generic init afterward.

## State and Persistence Behavior
Descriptors become mutable runtime objects with counters/locks after registration. Hardware state is programmed in DRA7xx PRM and MPU PRCM partitions. Many DRA7 domains allow OFF/ON only, with memory banks ON-only.

## Dependencies and Integration Points
It depends on DRA7xx PRM/PRCM headers, SoC detection, and the generic powerdomain framework. It integrates with `pm44xx.c`, DRA7 static dependency handling, remoteproc/media/display/GPU subsystems, and clockdomain registration.

## Risks
Variant-specific CUSTEFUSE handling is easy to get wrong because the same `custefuse_pwrdm` name maps to always-on or controllable descriptors. DRA7 has many accelerator domains; missing a domain can prevent driver PM or remoteproc operation.

## Test Signals
Boot DRA72x, DRA74x, and DRA76x variants, verify correct CUSTEFUSE descriptor selection and all accelerator domains register. Test suspend/idle, remoteproc DSP/EVE/IPU power cycling, display/GPU/CAM/VPE use, and PM debug counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains7xx_data.c -->
