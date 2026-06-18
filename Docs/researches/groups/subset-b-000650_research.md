# subset-b-000650 Research

This grouped report covers the OMAP2+ clockdomain and Clock Management files under `sources/distributed-fs/ceph-client/arch/arm/mach-omap2`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomain.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomain.c

Purpose: Implements the generic OMAP2/3/4 clockdomain framework. It maintains the global registered clockdomain list, binds static clockdomain data to powerdomains, dispatches hardware operations through a SoC-specific `struct clkdm_ops`, and provides the interface used by clock, hwmod, powerdomain, and CPU PM code.

Important APIs/types/functions: registration entry points are `clkdm_register_platform_funcs()`, `clkdm_register_clkdms()`, `clkdm_register_autodeps()`, and `clkdm_complete_init()`. Lookup/iteration APIs are `clkdm_lookup()`, `clkdm_for_each()`, and `clkdm_get_pwrdm()`. Dependency APIs cover wake and sleep dependencies with add/delete/read/clear variants. Runtime transition APIs are `clkdm_sleep()`, `clkdm_wakeup()`, `clkdm_allow_idle()`, `clkdm_deny_idle()`, `clkdm_clk_enable()`, `clkdm_clk_disable()`, `clkdm_hwmod_enable()`, and `clkdm_hwmod_disable()`. Context APIs are `clkdm_save_context()` and `clkdm_restore_context()`.

Control flow: SoC data first registers an operation table, then registers clockdomain descriptors. `_clkdm_register()` resolves `pwrdm.name` via `pwrdm_lookup()`, links the clockdomain into `clkdm_list`, and adds it to the powerdomain. `clkdm_complete_init()` denies idle on all registered clockdomains, resolves dependency names to pointers, clears hardware dependency registers, and on AM43xx registers a CPU PM notifier for off-mode context save/restore. Clock and hwmod enable paths increment `usecount`, call the backend `clkdm_clk_enable()`, and update powerdomain state; disable paths decrement and call the backend when the last user leaves.

State and persistence: Runtime state lives in the static `struct clockdomain` objects: `usecount`, `forcewake_count`, `_flags`, dependency usecounts, resolved dependency pointers, and `context`. `arch_clkdm` and `autodeps` are process-wide framework pointers. Hardware state is persisted only in CM/PRM registers; context save/restore is delegated to backend hooks and is invoked for all registered clockdomains by the CPU PM notifier or explicit callers.

Dependencies: Depends on `powerdomain.h` for powerdomain lookup, locking, state switching, and clockdomain association; `clock.h` for OMAP clock integration; Linux list, clk, notifier, and CPU PM infrastructure; and SoC predicates from `soc.h`.

Integration points: It is the central layer consumed by clock enable/disable code, OMAP hwmod module enable/disable code, powerdomain transition code, and SoC clockdomain data files. SoC backends in `cm2xxx.c`, `cm3xxx.c`, `cm33xx.c`, and `cminst44xx.c` supply the register-level operations.

Risks: Dependency add/delete usecounts are signed and can underflow if callers are unbalanced; wake dependency wrappers validate `wkdep_srcs`, but `clkdm_add_sleepdep()` and `clkdm_del_sleepdep()` look up through `wkdep_srcs` before calling sleepdep helpers, which is a fragile contract and may reject valid sleep-only data. Public wrappers such as `clkdm_sleep()` dereference `clkdm->pwrdm.ptr` before null checking, so callers must pass valid registered clockdomains. The framework assumes static data lifetime and does not unregister individual clockdomains.

Test signals: Boot-time validation should show all clockdomains registered with matching powerdomains and no dependency resolution warnings. Runtime tests should cover balanced clock/hwmod enable-disable cycles, dependency register changes, low-power entry/exit with context restore on AM43xx, and timeout-free device access after wake. Lockdep and WARN_ON signals are useful for usecount underflow and invalid state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomain.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomain.h

Purpose: Declares the OMAP clockdomain model, capability flags, dependency structures, backend operation table, public clockdomain APIs, and SoC init hooks.

Important APIs/types/functions: Defines `struct clockdomain`, `struct clkdm_dep`, `struct clkdm_autodep`, and `struct clkdm_ops`. Capability macros include `CLKDM_CAN_FORCE_SLEEP`, `CLKDM_CAN_FORCE_WAKEUP`, `CLKDM_CAN_ENABLE_AUTO`, `CLKDM_CAN_DISABLE_AUTO`, `CLKDM_NO_AUTODEPS`, `CLKDM_ACTIVE_WITH_MPU`, `CLKDM_MISSING_IDLE_REPORTING`, `CLKDM_STANDBY_FORCE_WAKEUP`, and combined `CLKDM_CAN_HWSUP`, `CLKDM_CAN_SWSUP`, `CLKDM_CAN_HWSUP_SWSUP`. It declares all public operations implemented by `clockdomain.c` plus per-SoC init functions.

Control flow: Static data files instantiate `struct clockdomain` with names, powerdomain names, CM offsets, flags, dependency arrays, and optional dependency bits. The framework resolves name fields into pointers during registration and completion, then dispatches through `struct clkdm_ops` callbacks selected by the SoC.

State and persistence: `struct clockdomain` contains persistent static descriptors plus mutable runtime fields: `_flags`, dependency pointers in arrays, `usecount`, `forcewake_count`, `node`, and `context`. These fields bridge software reference counting and hardware CM register context.

Dependencies: Includes `powerdomain.h` and `clock.h`, and forward declares `struct omap_hwmod`. Consumers include SoC clockdomain data, CM backend implementations, clock code, hwmod code, and PM code.

Integration points: Exported operation-table symbols (`omap2_clkdm_operations`, `omap3_clkdm_operations`, `omap4_clkdm_operations`, `am33xx_clkdm_operations`, `am43xx_clkdm_operations`) are registered by SoC-specific init functions. Shared 24xx dependency arrays and `wkup_common_clkdm` are exported for OMAP2420/2430 data.

Risks: The header encodes hardware layout assumptions in small integer fields (`u8` partitions, `u16` offsets, `u8` dep bits). Incorrect flag combinations can make the generic framework call unsupported backend transitions. The deprecated autodep model remains part of the ABI for OMAP3.

Test signals: Compile coverage across OMAP2, OMAP3, AM33xx, AM43xx, OMAP4, OMAP5, DRA7xx, and TI81xx configurations verifies conditional declarations. Runtime validation should confirm each static descriptor has a valid powerdomain name and correct flags for its backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2420_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2420_data.c

Purpose: Provides OMAP242x-specific static clockdomain descriptors and wake dependency data, then registers them with the generic clockdomain framework.

Important APIs/types/functions: Defines `mpu_2420_wkdeps`, `core_2420_wkdeps`, and clockdomains for `mpu`, `iva1`, `dsp`, `gfx`, `core_l3`, `core_l4`, and `dss`, plus the `clockdomains_omap242x[]` array and `omap242x_clockdomains_init()`.

Control flow: `omap242x_clockdomains_init()` registers `omap2_clkdm_operations`, registers the OMAP242x clockdomain array, and calls `clkdm_complete_init()`. The common `wkup_common_clkdm` comes from `clockdomains2xxx_3xxx_data.c`.

State and persistence: The descriptors are static `__initdata` inputs to boot-time registration; runtime state is stored in the registered `struct clockdomain` objects and OMAP24xx CM registers. Wake dependencies are resolved by name at completion time.

Dependencies: Includes `soc.h`, `clockdomain.h`, PRM module definitions, and 24xx CM register bit definitions. The descriptors depend on matching powerdomain names such as `mpu_pwrdm`, `dsp_pwrdm`, `gfx_pwrdm`, and `core_pwrdm`.

Integration points: Feeds the generic clockdomain framework for OMAP2420 systems and uses the OMAP2 CM backend from `cm2xxx.c` for CLKSTCTRL and wake dependency operations.

Risks: Static dependency names must exactly match registered clockdomain names. Several domains have hardware-supervised-only flags, so incorrect flags can block software sleep/wakeup. The OMAP2420 IVA/DSP split relies on hardware-specific dependency bits.

Test signals: OMAP2420 boot should show successful registration, dependency resolution, and no missing powerdomain errors. Functional clock gating, MPU retention checks, and wake from DSP/GFX/core activity exercise the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2420_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2430_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2430_data.c

Purpose: Provides OMAP243x clockdomain descriptors, including the modem domain, and registers them with OMAP2 clockdomain operations.

Important APIs/types/functions: Defines wake dependency arrays for core, MPU, and MDM, clockdomains for `mpu`, `mdm`, `dsp`, `gfx`, `core_l3`, `core_l4`, and `dss`, `clockdomains_omap243x[]`, and `omap243x_clockdomains_init()`.

Control flow: Initialization registers `omap2_clkdm_operations`, the OMAP243x descriptor array, and completes generic clockdomain setup. Core L3/L4 share the same dependency bit according to file comments, matching OMAP243x hardware limitations.

State and persistence: Static descriptors become runtime clockdomain objects. Dependency arrays store mutable resolved pointers and usecounts after init; actual state is controlled in OMAP2430 PRCM/CM registers.

Dependencies: Uses shared 24xx dependency arrays and `wkup_common_clkdm`, plus 24xx PRM/CM register bit macros. Powerdomain names include `mpu_pwrdm`, `mdm_pwrdm`, `dsp_pwrdm`, `gfx_pwrdm`, and `core_pwrdm`.

Integration points: Used by OMAP2430 early platform initialization. It connects OMAP243x-specific data to generic `clockdomain.c` and OMAP2 CM low-level operations.

Risks: The single dependency bit used for both core L3 and L4 requires care in dependency accounting. Missing or mismatched `mdm_clkdm` dependencies could affect modem wake latency and retention.

Test signals: OMAP2430 boot should resolve MDM, DSP, GFX, MPU, WKUP, core L3/L4 dependencies. Suspend/resume and modem-related wake scenarios are the strongest behavioral checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2430_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2xxx_3xxx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2xxx_3xxx_data.c

Purpose: Holds static clockdomain data shared by OMAP2xxx and OMAP3xxx families, avoiding duplication in SoC-specific files.

Important APIs/types/functions: Defines exported wake dependency arrays `gfx_24xx_wkdeps` and `dsp_24xx_wkdeps`, and exported `wkup_common_clkdm`.

Control flow: OMAP2420 and OMAP2430 data files include `wkup_common_clkdm` in their registration arrays and reference the shared dependency arrays from their static clockdomain descriptors. The generic framework resolves dependency names at `clkdm_complete_init()`.

State and persistence: The arrays are static and long-lived. Their `clkdm` pointers and usecounts are mutated after registration; `wkup_common_clkdm` receives normal runtime fields such as usecount and list node once registered.

Dependencies: Uses `prm2xxx_3xxx.h`, `cm-regbits-24xx.h`, and `clockdomain.h`. Depends on common clockdomain names like `core_l3_clkdm`, `core_l4_clkdm`, `mpu_clkdm`, and `wkup_clkdm`.

Integration points: This is a shared data-provider file for OMAP2-family clockdomain registration. It also exports symbols declared in `clockdomain.h`.

Risks: Because the same arrays are reused by multiple SoC files, future SoC-specific divergence should not be added here unless valid for all users. Name mismatches fail late during dependency resolution.

Test signals: OMAP2420 and OMAP2430 boot logs should not warn about unresolved shared dependencies. Wakeup domain behavior while MPU is active validates the `CLKDM_ACTIVE_WITH_MPU` flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2xxx_3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains33xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains33xx_data.c

Purpose: Defines AM33xx clockdomain descriptors and registers them with the AM33xx CM backend.

Important APIs/types/functions: Defines domains for L4LS, L3S, L4FW, L3, L4HS, OCPWP, PRUSS, CPSW, LCDC, 24MHz clock, WKUP, L3 AON, L4 WKUP AON, MPU, RTC, GFX L3, GFX L4LS, and CEFUSE. Provides `clockdomains_am33xx[]` and `am33xx_clockdomains_init()`.

Control flow: `am33xx_clockdomains_init()` registers `am33xx_clkdm_operations`, registers all AM33xx clockdomains, and completes initialization. There are no explicit dependency arrays; domains primarily use CM instance and clockdomain offset pairs with software-supervised capability flags.

State and persistence: Descriptors include `cm_inst` and `clkdm_offs` offsets into AM33xx CM. Runtime `context` is saved/restored by `cm33xx.c` for CLKTRCTRL state.

Dependencies: Includes `cm33xx.h`, `cm-regbits-33xx.h`, `prcm-common.h`, and `clockdomain.h`. Requires powerdomain names such as `per_pwrdm`, `wkup_pwrdm`, `mpu_pwrdm`, `rtc_pwrdm`, `gfx_pwrdm`, and `cefuse_pwrdm`.

Integration points: Used on AM33xx/AM335x systems by platform init. Its offsets feed AM33xx CM operations for force sleep/wakeup, hardware supervision, and module readiness.

Risks: A wrong `clkdm_offs` can make the backend write the wrong CLKSTCTRL register. Standby behavior has special handling in `cm33xx.c`, so domains requiring `CLKDM_STANDBY_FORCE_WAKEUP` must be flagged correctly.

Test signals: AM33xx boot should register all powerdomain mappings. Runtime checks include PRUSS/CPSW/LCDC enable-disable, standby wake, and PM tests that verify L4LS is not incorrectly forced asleep during standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains33xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains3xxx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains3xxx_data.c

Purpose: Provides OMAP3/AM35x clockdomain descriptors, wake dependencies, sleep dependencies, auto-dependency data, and SoC-revision-specific registration sets.

Important APIs/types/functions: Defines dependency arrays for SGX/GFX, PER, USBHOST, MPU, IVA2, CAM, DSS, NEON, and sleepdeps for DSS/PER/USBHOST/CAM/GFX. Defines clockdomains including MPU, NEON, IVA2, GFX/SGX, D2D, CORE L3/L4, DSS, CAM, USBHOST, PER, EMU, and DPLL domains. Provides `clockdomains_common[]`, `clockdomains_omap3430[]`, ES1/ES2+ variants, `clockdomains_am35x[]`, and `omap3xxx_clockdomains_init()`.

Control flow: Initialization registers `omap3_clkdm_operations`, registers common domains, conditionally registers OMAP3430 or AM35x-specific domain sets based on `soc_is_omap3430()` and `soc_is_am35xx()`, registers OMAP3 autodeps, and completes init.

State and persistence: Dependency arrays are resolved at runtime and their usecounts are adjusted by generic autodep and dependency APIs. OMAP3 CM registers hold CLKSTCTRL, wake, and sleep dependency state; broader CM context is saved by `cm3xxx.c`.

Dependencies: Uses `soc.h`, OMAP3 PRM/CM module definitions, `cm-regbits-34xx.h`, and `clockdomain.h`. Powerdomain names cover `mpu_pwrdm`, `neon_pwrdm`, `iva2_pwrdm`, `sgx_pwrdm`, `core_pwrdm`, `dss_pwrdm`, `cam_pwrdm`, `usbhost_pwrdm`, `per_pwrdm`, `emu_pwrdm`, and DPLL domains.

Integration points: This is the main OMAP3 clockdomain topology used by OMAP3 PM, clock, and hwmod code. It couples with `omap3_clkdm_operations` for sleepdep manipulation and deprecated autodeps needed by OMAP3 clock gating.

Risks: Many SoC revision conditionals mean an incorrect `soc_is_*` result can register the wrong SGX/GFX/USBHOST domain layout. Autodeps are deprecated and energy-costly but still required. `CLKDM_MISSING_IDLE_REPORTING` flags are critical for EMU-like domains to avoid unsafe powerdomain idling.

Test signals: OMAP3430 ES1, ES2+, and AM35x builds/boots should each register the expected variant domains. Suspend/resume, SGX/DSS/USBHOST activity, and DPLL idle behavior are important validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains43xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains43xx_data.c

Purpose: Defines AM43xx clockdomains using the OMAP4-style CM partition/instance layout with AM43xx-specific domain offsets.

Important APIs/types/functions: Defines domains for CEFUSE, MPU, L4LS, tamper, RTC, PRUSS, OCPWP, TSC, LCDC, DSS, L3 AON, EMIF, L4 WKUP AON, L3, L4 WKUP, CPSW, GFX, and L3S. Provides `clockdomains_am43xx[]` and `am43xx_clockdomains_init()`.

Control flow: Initialization registers `am43xx_clkdm_operations`, registers the AM43xx array, and completes generic initialization. The backend for AM43xx is implemented in `cminst44xx.c`, but with a reduced operation table compared with full OMAP4.

State and persistence: Static descriptors include `prcm_partition`, `cm_inst`, and `clkdm_offs`. AM43xx off-mode can lose clockdomain context; the generic layer installs a CPU PM notifier for AM43xx and uses backend context hooks when available.

Dependencies: Uses AM43xx CM/PRCM headers and OMAP4-style clockdomain infrastructure. Requires matching AM43xx powerdomain names for core, wakeup, graphics, RTC, and peripheral blocks.

Integration points: Bridges AM43xx data to the partitioned CM instance backend, enabling OMAP4-style CLKSTCTRL control on AM43xx.

Risks: Since `am43xx_clkdm_operations` lacks dependency and context callbacks in this snapshot, behavior differs from full OMAP4 and generic context calls may no-op or fail if invoked through absent hooks. Incorrect partition IDs are hazardous because the backend uses BUG_ON for invalid partitions.

Test signals: AM43xx boot should register all domains and complete init without partition faults. RTC-DDR suspend/resume and peripheral enable-disable cycles are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains43xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains44xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains44xx_data.c

Purpose: Defines OMAP44xx clockdomain topology, static dependency relationships, and the OMAP44xx clockdomain init sequence.

Important APIs/types/functions: Provides wake/sleep dependency arrays for D2D, Ducati, ISS, IVAHD, L3 DMA, DSS, GFX, L3INIT, L4 secure, MPU, and Tesla. Defines clockdomains for CEFUSE, L4 CFG, Tesla, GFX, IVAHD, L4 secure/per, ABE, L3 instr/init/emif/dma/DSS, D2D, MPU0/MPU1/MPU, L4 AO/WKUP, Ducati, L3_1/L3_2, ISS, and EMU. Provides `clockdomains_omap44xx[]` and `omap44xx_clockdomains_init()`.

Control flow: `omap44xx_clockdomains_init()` registers `omap4_clkdm_operations`, registers the OMAP44xx descriptor array, and completes initialization. Static dependency arrays are resolved into `OMAP4_CM_STATICDEP` bit operations by the backend.

State and persistence: Domain descriptors carry OMAP4 PRCM partition, CM instance, clockdomain offset, dependency bit, flags, and optional dependency arrays. Runtime context stores CLKSTCTRL state through `omap4_clkdm_save_context()`.

Dependencies: Includes OMAP4 CM1/CM2, CM regbits, PRCM partition headers, and clockdomain declarations. Depends on powerdomain data for MPU, ABE, core, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, CEFUSE, and wakeup domains.

Integration points: Used by OMAP4 platform initialization and OMAP4 PM/hwmod code. Integrates with `cminst44xx.c` for partitioned register reads/writes and static dependency manipulation.

Risks: Static dependency bit mappings must match hardware `STATDEP` fields. The large dependency graph is sensitive to missing names and can affect wake latency or prevent low-power entry. Partitioned register access will BUG on invalid base setup.

Test signals: OMAP44xx boot should register all domains and resolve dependencies. Device tests for Ducati, DSS, GFX, IVAHD, L3INIT USB, and suspend/resume exercise the topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains44xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains54xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains54xx_data.c

Purpose: Defines OMAP54xx clockdomains and wake/sleep dependencies for CM_CORE_AON and CM_CORE based systems.

Important APIs/types/functions: Defines dependencies for C2C, CAM, DMA, DSP, DSS, GPU, IPU, IVA, L3INIT, L4SEC, MIPIEXT, and MPU. Defines domains such as L4SEC, IVA, MIPIEXT, L3MAIN1/2, CUSTEFUSE, IPU, L4CFG, ABE, DSS, DSP, C2C, L4PER, GPU, WKUPAON, MPU0/1/MPU, COREAON, L3INIT, DMA, L3INSTR, EMIF, EMU, and CAM. Provides `clockdomains_omap54xx[]` and `omap54xx_clockdomains_init()`.

Control flow: The init function registers OMAP4-style clockdomain operations, registers the OMAP54xx array, and completes setup. Dependency arrays are used by OMAP4-style static dependency operations.

State and persistence: Static descriptors store PRCM partition IDs and CM instance/offset data from `cm1_54xx.h` and `cm2_54xx.h`. Runtime save/restore uses OMAP4-style CLKSTCTRL context handling where available.

Dependencies: Includes OMAP54xx CM1/CM2 headers, OMAP54xx regbits, PRCM common headers, and clockdomain declarations. Powerdomain names must align with OMAP5 powerdomain data.

Integration points: Feeds the OMAP5 clockdomain framework and PM code with CM_CORE_AON/CM_CORE topology.

Risks: OMAP54xx has many interconnect and accelerator dependencies; missing a dependency can cause peripheral access latency or unsafe domain idling. Generated register macros should be updated via hardware database flow rather than hand edits.

Test signals: OMAP5 boot, accelerator/peripheral activity tests, and suspend/resume should validate dependency graph and CLKSTCTRL behavior for MPU, IPU, DSP, IVA, DSS, GPU, and L3INIT domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains54xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains7xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains7xx_data.c

Purpose: Defines DRA7xx clockdomain topology, including DSP, EVE, IPU, IVA, GPU, display, camera, PCIe, GMAC, and interconnect domains.

Important APIs/types/functions: Provides many wake/sleep dependency arrays for CAM, DMA, DSP1/2, DSS, EVE1-4, GMAC, GPU, IPU1/2, IVA, L3INIT, L4PER2, L4SEC, MPU, PCIe, and VPE. Defines clockdomains for L4PER2/3, MPU0/1/MPU, IVA, COREAON, IPU/IPU1/IPU2, L3INIT, L4SEC, L3MAIN1, VPE, CUSTEFUSE, GMAC, L4CFG, DMA, RTC, PCIe, ATL, L3INSTR, DSS, EMIF, EMU, DSP1/2, CAM, L4PER, GPU, EVE1-4, and WKUPAON. Provides `clockdomains_dra7xx[]` and `dra7xx_clockdomains_init()`.

Control flow: Initialization registers `omap4_clkdm_operations`, registers all DRA7xx domains, and completes generic setup. The OMAP4-style backend writes CLKSTCTRL and STATICDEP fields via CM_CORE_AON/CM_CORE partitions.

State and persistence: Descriptors are static and source generated. Mutable state is in generic `struct clockdomain` fields and DRA7xx CM registers. Dependency arrays resolve to pointers and usecounts after init.

Dependencies: Includes DRA7xx CM1/CM2 headers, DRA7xx regbits, PRCM common headers, and clockdomain APIs. Depends on DRA7xx powerdomain definitions matching the descriptor names.

Integration points: Used by DRA7 platform PM and hwmod/clock operations; its broad accelerator topology is central to low-power behavior on Jacinto/DRA7 devices.

Risks: This is the largest dependency graph in the subset. Generated offsets and STATDEP bits must remain synchronized with hardware data. Missing EVE/DSP/IPU/PCIe/GMAC dependencies may cause wake failures or block retention/off modes.

Test signals: DRA7 boot plus driver activity across display, camera, PCIe, GMAC, IPU, DSP, and EVE blocks. Suspend/resume and runtime PM should verify no unresolved dependency warnings or CM timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains7xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains81xx_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains81xx_data.c

Purpose: Defines TI814x and TI816x clockdomains using the AM33xx-style CM backend and TI81xx-specific CM offsets.

Important APIs/types/functions: Defines common TI81xx ALWON/default/MMU domains and TI816x-specific MPU, GEM, IVAHD0-2, SGX, default L3 medium, Ducati, and PCI domains. Provides separate arrays `clockdomains_ti814x[]` and `clockdomains_ti816x[]`, with init functions `ti814x_clockdomains_init()` and `ti816x_clockdomains_init()`.

Control flow: Each init function registers `am33xx_clkdm_operations`, registers the appropriate SoC-specific array, and completes initialization.

State and persistence: Descriptors store TI81xx CM module offsets in `cm_inst` and clockdomain offsets in `clkdm_offs`. Runtime state is handled through the AM33xx CM register model.

Dependencies: Includes `cm81xx.h`, `cm-regbits-33xx.h`, `prcm-common.h`, and `clockdomain.h`. Requires TI814x/TI816x powerdomain names such as `alwon_pwrdm`, `default_pwrdm`, `active_pwrdm`, `ivahd*_pwrdm`, and `sgx_pwrdm`.

Integration points: Supports DM814/DM816 platform clockdomain registration and reuses the AM33xx operation table for CLKSTCTRL control.

Risks: TI814x and TI816x arrays share several descriptors but differ in included domains; wrong init selection would expose unavailable domains or omit needed ones. Offset reuse such as ALWON L3 medium/Ethernet requires careful hardware validation.

Test signals: DM814/DM816 boot should register the correct array. Ethernet, SATA, Ducati, IVAHD, SGX, and PCI activity are useful domain-specific checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains81xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-24xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-24xx.h

Purpose: Defines OMAP24xx Clock Management bit masks and shifts used by OMAP2 CM code and static clockdomain data.

Important APIs/types/functions: Provides masks/shifts for OMAP24xx autostate, functional clock enable/status fields, APLL/DPLL autoidle fields, core clock source, and CLKSTCTRL automatic mode values `OMAP24XX_CLKSTCTRL_DISABLE_AUTO` and `OMAP24XX_CLKSTCTRL_ENABLE_AUTO`.

Control flow: This header has no executable flow. Its macros are consumed by `cm2xxx.c`, `cm2xxx.h`, and OMAP2420/2430 clockdomain data to compose register reads/writes and dependency bits.

State and persistence: No software state. It describes persistent hardware register bit positions in the OMAP24xx CM block.

Dependencies: Standalone guarded header; included by OMAP2-specific CM and clockdomain files.

Integration points: Supports DPLL/APLL autoidle control, module status polling, DSS/UART/MMC/McSPI retention gating checks, and OMAP24xx CLKSTCTRL hardware-supervision toggling.

Risks: Bit definitions are hardware contracts; incorrect masks can break clock enable status, retention decisions, and PLL autoidle. Some macros are SoC-specific to OMAP2420 or OMAP2430 and should not be used interchangeably.

Test signals: OMAP2420/2430 compile coverage and runtime checks for DPLL autoidle, module readiness, MPU retention allowed logic, and clockdomain auto mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-24xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-33xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-33xx.h

Purpose: Defines AM33xx CM register bit masks and shifts, generated from hardware data.

Important APIs/types/functions: Provides CLKOUT2, DPLL divider/multiplier/enable, HSDIVIDER, IDLEST, MODULEMODE, CLKTRCTRL, optional clock enable, STM/TRC, and DPLL status fields. Key values used by `cm33xx.c` are `AM33XX_IDLEST_MASK`, `AM33XX_IDLEST_SHIFT`, `AM33XX_MODULEMODE_MASK`, `AM33XX_MODULEMODE_SHIFT`, `AM33XX_CLKTRCTRL_MASK`, and `AM33XX_CLKTRCTRL_SHIFT`.

Control flow: No executable flow. AM33xx CM code uses these macros to poll module state, enable/disable module mode, and save/restore clockdomain transition mode.

State and persistence: No software state; represents hardware register fields.

Dependencies: Standalone guarded header included by `cm33xx.h`, `cm33xx.c`, and AM33xx/TI81xx clockdomain data.

Integration points: Critical to AM33xx module readiness/idle waits, CLKSTCTRL mode writes, and module enable/disable through CM_*_CLKCTRL registers.

Risks: Generated definitions must remain synchronized with AM33xx hardware databases. Misusing masks with OMAP34xx mode constants is intentional in this code but requires matching field encoding.

Test signals: AM33xx/TI81xx boot with module enable/disable should avoid CM timeouts and imprecise external aborts. Build tests should include suspend-enabled and non-suspend configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-33xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-34xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-34xx.h

Purpose: Defines OMAP3430/AM35xx CM register masks, shifts, and CLKSTCTRL mode encodings.

Important APIs/types/functions: Includes IVA2, MPU, CORE, GFX/SGX, DSS, CAM, PER, EMU, NEON, USBHOST status and CLKTRCTRL fields, plus `OMAP34XX_CLKSTCTRL_DISABLE_AUTO`, `OMAP34XX_CLKSTCTRL_FORCE_SLEEP`, `OMAP34XX_CLKSTCTRL_FORCE_WAKEUP`, and `OMAP34XX_CLKSTCTRL_ENABLE_AUTO`.

Control flow: No executable flow. `cm3xxx.c`, `cm33xx.c`, and `cminst44xx.c` use the mode constants to write CLKSTCTRL fields; OMAP3 data uses the masks for clockdomain descriptors.

State and persistence: No software state. Defines CM hardware field layout and mode values.

Dependencies: Standalone guarded header used by OMAP3 and by newer backends where CLKSTCTRL encodings are shared.

Integration points: Supports OMAP3 autodeps, sleepdeps, force sleep/wakeup, hardware supervision, and context save/restore.

Risks: This header mixes OMAP3430 and AM35xx fields and ES-specific macros. Incorrect selection can break SGX/GFX or USBHOST handling across silicon revisions.

Test signals: OMAP3430 ES1/ES2+, AM35x, AM33xx, and OMAP4-style builds should compile and use expected CLKSTCTRL encodings. Runtime CM timeout absence validates status/mode fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-34xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-44xx.h

Purpose: Defines OMAP44xx CM register bit shifts and masks, especially static dependency bits and common CLKCTRL/CLKSTCTRL fields.

Important APIs/types/functions: Provides `OMAP4430_*_STATDEP_SHIFT` values for ABE, Ducati, IVAHD, MEMIF, L3/L4 domains, DSS, GFX, L3INIT, TESLA, and wakeup domains, plus `OMAP4430_IDLEST_MASK`, `OMAP4430_CLKTRCTRL_MASK`, and `OMAP4430_MODULEMODE_MASK`.

Control flow: No executable logic. Clockdomain data uses STATDEP shifts as `dep_bit` values, while the OMAP4 CM backend uses local equivalent masks for IDLEST, CLKTRCTRL, and MODULEMODE.

State and persistence: No software state. Encodes OMAP44xx CM hardware bit positions.

Dependencies: Standalone guarded generated header. Included by OMAP44xx clockdomain data and related CM code.

Integration points: Enables OMAP4 static dependency register programming through `OMAP4_CM_STATICDEP`.

Risks: Static dependency shifts are central to wake/sleep behavior; mismatched values can either prevent low-power entry or fail to wake dependent domains. Generated-file comments imply edits should stay coordinated with hardware database generation.

Test signals: OMAP4 boot dependency resolution, accelerator/peripheral wake tests, and suspend/resume validate the shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-54xx.h

Purpose: Defines OMAP54xx CM register masks and shifts for DPLL, clock selection, optional clocks, and static dependency fields.

Important APIs/types/functions: Provides DPLL masks, clock select/divider shifts, optional functional clock gate shifts, and STATDEP shifts for IPU, DSP, IVA, ABE, EMIF, L3MAIN, L3INIT, DSS, GPU, L4CFG, L4PER, L4SEC, and WKUPAON.

Control flow: No executable flow. OMAP54xx clockdomain data uses these macros in dependency bits and CM-related code uses the clock field masks.

State and persistence: No software state; documents generated hardware field layout.

Dependencies: Standalone guarded generated header used by OMAP5/54xx CM data.

Integration points: Supports OMAP54xx clockdomain static dependency programming and clock/DPLL configuration.

Risks: The header contains many generated masks with narrow hardware meanings. Manual edits risk desynchronizing from hardware databases and breaking clock tree or dependency behavior.

Test signals: OMAP5 builds, DPLL/clock selection tests, and runtime PM coverage for IPU/DSP/IVA/GPU/DSS/L3INIT domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-7xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-7xx.h

Purpose: Defines DRA7xx static dependency bit shifts for clockdomain relationships.

Important APIs/types/functions: Provides `DRA7XX_*_STATDEP_SHIFT` macros for ATL, CAM, DSP1/2, DSS, EMIF, EVE1-4, GMAC, GPU, IPU/IPU1/IPU2, IVA, L3INIT, L3MAIN1, L4CFG, L4PER/L4PER2/L4PER3, L4SEC, PCIe, VPE, and WKUPAON.

Control flow: No executable flow. DRA7xx clockdomain data assigns these shifts to `dep_bit` fields, and OMAP4-style backend code uses them when manipulating STATICDEP registers.

State and persistence: No software state; hardware field definitions only.

Dependencies: Standalone generated header included by DRA7xx clockdomain data.

Integration points: Supports DRA7xx wake/sleep dependency programming across CPU, accelerator, media, networking, and interconnect domains.

Risks: A wrong shift can silently program the wrong dependency bit. Because DRA7xx has many accelerator domains, errors may surface only in specific device wake or suspend scenarios.

Test signals: DRA7xx runtime PM, suspend/resume, PCIe/GMAC/CAM/DSS/GPU/IPU/DSP/EVE activity tests, and dependency resolution warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-7xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm.h

Purpose: Declares the common OMAP Clock Management interface, timeout constants, CM base globals, low-level operation table, and dispatcher functions.

Important APIs/types/functions: Defines `MAX_MODULE_READY_TIME`, `MAX_MODULE_DISABLE_TIME`, `struct cm_ll_data`, globals `cm_base` and `cm2_base`, and dispatcher APIs `cm_split_idlest_reg()`, `omap_cm_wait_module_ready()`, `omap_cm_wait_module_idle()`, `omap_cm_module_enable()`, `omap_cm_module_disable()`, `omap_cm_xlate_clkctrl()`, `cm_register()`, `cm_unregister()`, `omap_cm_init()`, and `omap2_cm_base_init()`.

Control flow: SoC-specific CM backends fill `struct cm_ll_data` and call `cm_register()`. Shared hwmod/clock code calls the dispatchers without needing to know the SoC register model.

State and persistence: Declares global CM base mappings and a function-pointer interface; runtime storage is implemented in `cm_common.c`.

Dependencies: Includes TI clock provider definitions and `prcm-common.h` outside assembler context.

Integration points: This is the ABI between platform-independent OMAP CM users and per-SoC CM implementations.

Risks: Missing low-level function pointers return `-EINVAL` or `0` with warnings, so callers must handle unavailable operations. Timeout values are hardware-sensitive and too-short waits can cause false failures.

Test signals: Build coverage for each SoC backend and runtime absence of `WARN_ONCE` from missing CM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_44xx.h

Purpose: Defines OMAP44xx CM1 base, register address helper, CM1 instance offsets, and clockdomain offsets.

Important APIs/types/functions: Macros include `OMAP4430_CM1_BASE`, `OMAP44XX_CM1_REGADDR()`, CM1 instances for OCP socket, CKGEN, MPU, TESLA, and ABE, plus CDOFFS for MPU, TESLA, and ABE clockdomains.

Control flow: No executable flow. Static clockdomain data uses instance and CDOFFS macros; OMAP4 register code combines them with partition bases.

State and persistence: No software state; hardware address definitions only.

Dependencies: Uses `OMAP2_L4_IO_ADDRESS` from included platform address infrastructure through users.

Integration points: Used by OMAP44xx clockdomain data and OMAP4 CM instance backend.

Risks: Generated comments note naming alignment issues. Wrong base/offset values make partitioned CM access hit incorrect registers.

Test signals: OMAP44xx boot, ABE/Tesla/MPU clockdomain transitions, and no OMAP4 CM BUG_ON during register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_54xx.h

Purpose: Defines OMAP54xx CM_CORE_AON base, register helper, always-on CM instances, and clockdomain offsets.

Important APIs/types/functions: Provides `OMAP54XX_CM_CORE_AON_BASE`, `OMAP54XX_CM_CORE_AON_REGADDR()`, instances for OCP socket, CKGEN, MPU, DSP, and ABE, and CDOFFS for MPU, DSP, and ABE.

Control flow: No executable flow; consumed by OMAP54xx static clockdomain data.

State and persistence: No software state. The macros describe persistent hardware register addresses.

Dependencies: Used with OMAP2 L4 IO address mapping and OMAP4-style CM partition access.

Integration points: Enables OMAP5 CM_CORE_AON domain registration and register access.

Risks: Wrong always-on CM offsets can break MPU/DSP/ABE clockdomain management and suspend/resume.

Test signals: OMAP5 boot and runtime PM for MPU, DSP, and ABE domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_7xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_7xx.h

Purpose: Defines DRA7xx CM_CORE_AON base, register helper, instance offsets, and clockdomain offsets for always-on and accelerator domains.

Important APIs/types/functions: Provides `DRA7XX_CM_CORE_AON_BASE`, `DRA7XX_CM_CORE_AON_REGADDR()`, instances for OCP socket, CKGEN, MPU, DSP1, IPU, DSP2, EVE1-4, RTC, and VPE, and matching CDOFFS values.

Control flow: No executable flow. DRA7xx clockdomain data uses these macros to populate `cm_inst` and `clkdm_offs`.

State and persistence: No software state; hardware map definitions only.

Dependencies: Used by DRA7xx clockdomain data with OMAP4-style CM backend.

Integration points: Provides CM1 address layout for DRA7xx PM and clockdomain code.

Risks: Accelerator-heavy domains make offset errors costly and potentially device-specific. Generated-file workflow should be preserved for updates.

Test signals: DRA7xx boot plus DSP/IPU/EVE/RTC/VPE runtime PM and suspend/resume validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_7xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_44xx.h

Purpose: Defines OMAP44xx CM2 base, register helper, CM2 instance offsets, and core/peripheral clockdomain offsets.

Important APIs/types/functions: Provides `OMAP4430_CM2_BASE`, `OMAP44XX_CM2_REGADDR()`, instances for OCP socket, CKGEN, ALWAYS_ON, CORE, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, and CEFUSE, plus CDOFFS for ALWON, L3, Ducati, SDMA, MEMIF, D2D, L4CFG, L3INSTR, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, L4SEC, and CEFUSE.

Control flow: No executable flow. Used as register-coordinate input to OMAP44xx clockdomain descriptors.

State and persistence: No software state; hardware address constants only.

Dependencies: Used with PRCM partition IDs and OMAP4 CM instance backend.

Integration points: Central to OMAP44xx CM2 domain control for core and peripheral domains.

Risks: CM2 covers many high-use peripherals; wrong offsets can cause broad device failures or register aborts.

Test signals: OMAP44xx boot and runtime PM for core interconnect, Ducati, IVAHD, DSS, GFX, L3INIT, L4PER, and CEFUSE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_54xx.h

Purpose: Defines OMAP54xx CM_CORE base, register helper, CM_CORE instance offsets, and clockdomain offsets.

Important APIs/types/functions: Provides `OMAP54XX_CM_CORE_BASE`, `OMAP54XX_CM_CORE_REGADDR()`, instances for OCP socket, CKGEN, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, and CUSTEFUSE, plus CDOFFS for L3MAIN1/2, IPU, DMA, EMIF, C2C, L4CFG, L3INSTR, MIPIEXT, L4PER, L4SEC, IVA, CAM, DSS, GPU, L3INIT, and CUSTEFUSE.

Control flow: No executable flow; consumed by OMAP54xx clockdomain data.

State and persistence: No software state.

Dependencies: Used with OMAP4-style partitioned CM access.

Integration points: Provides core CM address layout for OMAP5 clockdomain and PM code.

Risks: Incorrect generated offsets affect major interconnect and multimedia domains. Updates should track hardware database output.

Test signals: OMAP5 boot, module readiness waits, and runtime PM for IPU/DMA/EMIF/C2C/MIPIEXT/L4/L3/IVA/CAM/DSS/GPU/L3INIT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_7xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_7xx.h

Purpose: Defines DRA7xx CM_CORE base, register helper, CM_CORE instance offsets, and clockdomain offsets.

Important APIs/types/functions: Provides `DRA7XX_CM_CORE_BASE`, `DRA7XX_CM_CORE_REGADDR()`, instances for OCP socket, CKGEN, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, CUSTEFUSE, and L4PER. Defines CDOFFS for L3MAIN1, IPU2, DMA, EMIF, ATL, L4CFG, L3INSTR, IVA, CAM, DSS, GPU, L3INIT, PCIe, GMAC, CUSTEFUSE, L4PER, L4SEC, L4PER2, and L4PER3.

Control flow: No executable flow. DRA7xx clockdomain descriptors use these offsets.

State and persistence: No software state; hardware register map only.

Dependencies: Used with DRA7xx regbits and OMAP4-style CM backend.

Integration points: Supports DRA7xx CM2/core domain control for interconnect, media, networking, PCIe, and peripheral blocks.

Risks: The CKGEN instance offset differs from simpler OMAP5 layout (`0x0104`), so copy-paste from other families is unsafe. Wrong CDOFFS values can affect only one accelerator path and be hard to diagnose.

Test signals: DRA7xx boot and runtime PM across PCIe, GMAC, ATL, L4PER2/3, GPU, DSS, CAM, and IVA domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_7xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.c

Purpose: Implements OMAP2xxx-specific CM low-level operations and clockdomain backend behavior.

Important APIs/types/functions: Internal helpers include `_write_clktrctrl()`, `omap2xxx_cm_is_clkdm_in_hwsup()`, `omap2xxx_cm_clkdm_enable_hwsup()`, `omap2xxx_cm_clkdm_disable_hwsup()`, `_omap2xxx_set_dpll_autoidle()`, `omap2xxx_cm_split_idlest_reg()`, and `omap2xxx_cm_wait_module_ready()`. Public functions include DPLL autoidle setters, `omap2xxx_cm_fclks_active()`, `omap2xxx_cm_mpu_retention_allowed()`, core clock queries, divider programming, and `omap2xxx_cm_init()`. Exports `struct clkdm_ops omap2_clkdm_operations`.

Control flow: The backend maps generic clockdomain calls to OMAP2 module register accesses through `omap2_cm_read_mod_reg()` and `omap2_cm_write_mod_reg()`. Clock enable/disable checks hwsup state and forces wake/sleep where supported. `omap2xxx_cm_init()` registers `omap2xxx_cm_ll_data` with the common CM layer.

State and persistence: Software state is minimal; it writes CM registers directly. DPLL/APLL autoidle and divider settings persist in hardware registers. Common CM stores the registered operation table pointer.

Dependencies: Includes PRM2xxx, CM common headers, OMAP24xx bit definitions, and clockdomain APIs. It reuses wake dependency helpers declared elsewhere for OMAP2.

Integration points: Used by OMAP2420/2430 clockdomain data and the common CM dispatchers for module readiness and legacy IDLEST register splitting.

Risks: The DPLL setter names appear counterintuitive: `omap2xxx_cm_set_dpll_disable_autoidle()` writes low-power stop and `omap2xxx_cm_set_dpll_auto_low_power_stop()` writes disable, so callers must match historical semantics. Module readiness uses OMAP2 polarity where enabled means the IDLEST bit is set.

Test signals: OMAP2 boot should initialize CM, poll IDLEST successfully, and control DPLL autoidle. MPU retention allowed logic should respond to active MMC/UART/McSPI/DSS clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.h

Purpose: Declares OMAP2xxx CM address macros, OMAP2-specific register offsets, IDLEST polarity value, and public OMAP2 CM helpers.

Important APIs/types/functions: Provides `OMAP2420_CM_REGADDR()`, `OMAP2430_CM_REGADDR()`, offsets for `OMAP24XX_CM_FCLKEN2`, `OMAP24XX_CM_ICLKEN4`, `OMAP24XX_CM_AUTOIDLE4`, `OMAP24XX_CM_IDLEST4`, `OMAP24XX_CM_IDLEST_VAL`, and prototypes for OMAP2 DPLL/clock/retention/divider helpers plus `omap2xxx_cm_init()`.

Control flow: No executable flow beyond macro expansion and inline inclusion from shared `cm2xxx_3xxx.h`.

State and persistence: No software state; maps hardware offsets and declares functions implemented in `cm2xxx.c`.

Dependencies: Includes `prcm-common.h` and shared OMAP2/3 CM definitions.

Integration points: Used by OMAP2 CM backend, clock code, and PM code that needs OMAP2-specific CM helpers.

Risks: Address macros must be used with the correct OMAP2420 vs OMAP2430 base. `OMAP24XX_CM_IDLEST_VAL` differs from OMAP3 and is important for readiness logic.

Test signals: OMAP2 builds and runtime CM IDLEST polling, DPLL autoidle, and divider programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx_3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx_3xxx.h

Purpose: Provides CM register offsets and inline register accessors shared by OMAP2xxx and OMAP3xxx.

Important APIs/types/functions: Defines common offsets for FCLKEN, ICLKEN, IDLEST, AUTOIDLE, CLKSEL, and CLKSTCTRL registers. Provides inline `omap2_cm_read_mod_reg()`, `omap2_cm_write_mod_reg()`, `omap2_cm_rmw_mod_reg_bits()`, `omap2_cm_read_mod_bits_shift()`, `omap2_cm_set_mod_reg_bits()`, and `omap2_cm_clear_mod_reg_bits()`. Also defines shared GFX clock/status bit macros.

Control flow: Inline accessors compute `cm_base.va + module + idx`, perform relaxed MMIO reads/writes, and implement read-modify-write bit operations.

State and persistence: No independent state. Operations manipulate CM hardware registers directly through global `cm_base`.

Dependencies: Includes `cm.h` and Linux IO primitives outside assembler context.

Integration points: Used heavily by `cm2xxx.c`, `cm3xxx.c`, and related clock/PM code as the OMAP2/3 register access layer.

Risks: Callers are responsible for locking around read-modify-write. Bad module offsets or uninitialized `cm_base.va` can cause invalid MMIO. The header is not suitable for OMAP4+ CM layout.

Test signals: OMAP2/3 boot with successful CM mapping, module readiness polling, sleepdep/wkdep changes, and clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx_3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.c

Purpose: Implements AM33xx CM register access, module enable/disable, module readiness/idle polling, clockdomain operations, and clockdomain context save/restore.

Important APIs/types/functions: Internal helpers include `am33xx_cm_read_reg()`, `am33xx_cm_write_reg()`, `am33xx_cm_rmw_reg_bits()`, `_clkctrl_idlest()`, `_is_module_ready()`, `_clktrctrl_write()`, hwsup/force sleep/wakeup helpers, module enable/disable functions, and xlate. Exports `struct clkdm_ops am33xx_clkdm_operations` and registers `am33xx_cm_ll_data` through `am33xx_cm_init()`.

Control flow: Common CM dispatch calls AM33xx functions for module mode writes and IDLEST polling. Generic clockdomain calls map to CLKSTCTRL writes through `cm_inst` and `clkdm_offs`. Clock disable may force sleep if the domain is not in hardware-supervised mode; standby mode avoids forcing flagged domains asleep.

State and persistence: Hardware state lives in AM33xx CM registers. `am33xx_clkdm_save_context()` stores CLKTRCTRL bits into `clkdm->context`, and restore dispatches to deny idle, sleep, wakeup, or allow idle.

Dependencies: Includes AM33xx CM offsets, AM33xx/OMAP34xx regbits, PRM33xx, clockdomain APIs, and optionally suspend state.

Integration points: Used by AM33xx and TI81xx clockdomain data and by common CM APIs for hwmod module control.

Risks: Module access before `_is_module_ready()` can cause imprecise external aborts, which this file explicitly guards against. Standby-specific L4LS handling depends on `pm_suspend_target_state` and correct flags. The code assumes `cm_base.va` is initialized.

Test signals: AM33xx module enable/disable should reach functional/disabled IDLEST within timeout. Standby and suspend/resume should preserve clockdomain mode and avoid L4LS sleep-related wake failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.h

Purpose: Defines AM33xx CM base address, register address helper, CM instance offsets, selected CLKSTCTRL/CLKCTRL register offsets, and the AM33xx CM init prototype.

Important APIs/types/functions: Provides `AM33XX_CM_BASE`, `AM33XX_CM_REGADDR()`, instances for PER, WKUP, DPLL, MPU, DEVICE, RTC, GFX, and CEFUSE, plus offsets for L4LS, L3S, L4FW, L3, EMIF, L4HS, OCPWP, PRUSS, CPSW, LCDC, 24MHz, WKUP, L3 AON, L4 WKUP AON, GFX, RTC, and CEFUSE registers.

Control flow: No executable flow; macros feed static data and AM33xx CM backend register calculations.

State and persistence: No software state; hardware address map only.

Dependencies: Includes `cm.h`, `cm-regbits-33xx.h`, and `prcm-common.h`.

Integration points: Used by `cm33xx.c` and `clockdomains33xx_data.c`.

Risks: The file only lists selected registers needed by this code. Adding new domains/modules requires matching offsets from hardware data.

Test signals: AM33xx compile and boot, especially peripherals mapped through the listed offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.c

Purpose: Implements OMAP3 CM operations, OMAP3 clockdomain backend behavior, sleep dependency handling, and CM context save/restore for low-power states.

Important APIs/types/functions: Includes CLKTRCTRL helpers, `omap3xxx_cm_wait_module_ready()`, `omap3xxx_cm_split_idlest_reg()`, sleepdep add/delete/read/clear operations, force sleep/wakeup and hwsup operations, `omap3_clkdm_operations`, `struct omap3_cm_regs`, `omap3_cm_save_context()`, `omap3_cm_restore_context()`, `omap3_cm_save_scratchpad_contents()`, and `omap3xxx_cm_init()`.

Control flow: OMAP3 CM dispatchers poll IDLEST with OMAP3 polarity, split legacy IDLEST register addresses, and control CLKSTCTRL fields. Clock enable/disable handles missing idle reporting, temporarily disables hwsup while changing autodeps, and uses force wake/sleep when in software-supervised mode.

State and persistence: OMAP3 CM context is saved into static `cm_context`, which covers clock selects, enables, autoidle, CLKSTCTRL, sleepdeps, and CLKOUT control. Scratchpad save writes a DPLL/clock subset for ROM-assisted resume. Runtime clockdomain state remains in generic `struct clockdomain`.

Dependencies: Uses OMAP2/3 PRM/CM headers, OMAP34xx regbits, generic clockdomain APIs, and `omap2_clk_legacy_provider_init()`.

Integration points: Backend for `clockdomains3xxx_data.c`, common CM dispatch, OMAP3 PM suspend/resume, and clock provider initialization.

Risks: Context list is broad and order-sensitive; omitted registers can break resume. Erratum i671 requires special PER DPLL autoidle handling. Autodep manipulation while in hwsup is delicate.

Test signals: OMAP3 suspend/resume, retention/off-mode resume, SGX/DSS/CAM/PER/USBHOST enable-disable, and DPLL scratchpad restore should be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.h

Purpose: Defines OMAP3 CM address helper, OMAP3-specific CM register offsets, IDLEST value, context function prototypes, and OMAP3 CM init prototype.

Important APIs/types/functions: Provides `OMAP34XX_CM_REGADDR()`, global offsets like `OMAP3430_CM_SYSCONFIG`, `OMAP3430_CM_POLCTRL`, `OMAP3_CM_CLKOUT_CTRL_OFFSET`, OMAP3 PLL/CLKEN/CLKSEL/SLEEPDEP/CLKSTST offsets, `OMAP34XX_CM_IDLEST_VAL`, and prototypes for OMAP3 context save/restore/scratchpad and `omap3xxx_cm_init()`.

Control flow: No executable flow; macros are consumed by `cm3xxx.c` and related clock/PM code.

State and persistence: No software state in header; declares context functions implemented in `cm3xxx.c`.

Dependencies: Includes `prcm-common.h` and shared OMAP2/3 CM definitions.

Integration points: OMAP3 CM backend, PM resume code, and clock initialization.

Risks: Several register offsets alias common offsets with OMAP3-specific meanings. Silicon revision differences are handled elsewhere, so callers must choose appropriate macros.

Test signals: OMAP3 build and resume tests covering CM context and scratchpad handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm44xx.h

Purpose: Provides common OMAP4+ CM definitions shared by CM1/CM2 layouts and declares OMAP4 CM initialization.

Important APIs/types/functions: Defines `OMAP4_CM_CLKSTCTRL`, `OMAP4_CM_STATICDEP`, and `omap4_cm_init()`.

Control flow: No executable flow. `cminst44xx.c` uses the register offsets for CLKSTCTRL and STATICDEP access.

State and persistence: No software state.

Dependencies: Includes `prcm-common.h` and `cm.h`.

Integration points: Shared by OMAP4, OMAP5, DRA7xx, and AM43xx partitioned CM code.

Risks: These offsets are assumed by all OMAP4-style clockdomain data. Incorrect values would break all CLKSTCTRL and dependency operations.

Test signals: OMAP4-style SoC boot and runtime PM operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm81xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm81xx.h

Purpose: Defines TI81xx CM module offsets and clockdomain register offsets for TI814x/TI816x.

Important APIs/types/functions: Provides common module offsets for ACTIVE, DEFAULT, ALWON, and SGX; TI816x IVAHD module offsets; and offsets for ALWON L3 slow/medium/fast, Ethernet, MMU, MMUCFG, MPU, GEM, IVAHD0-2, SGX, default L3 medium/slow, PCI, Ducati, and SATA clockdomains.

Control flow: No executable flow. TI81xx clockdomain data uses these constants as `cm_inst` and `clkdm_offs`.

State and persistence: No software state; hardware register offset definitions only.

Dependencies: Standalone guarded header.

Integration points: Used by `clockdomains81xx_data.c` with `am33xx_clkdm_operations`.

Risks: TI814x/TI816x share some offsets but not all domains. Wrong SoC use can access unavailable modules.

Test signals: TI814x/TI816x boot and runtime PM for ALWON, default, IVAHD, SGX, SATA, PCI, and Ethernet domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm81xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm_common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm_common.c

Purpose: Implements the common OMAP CM dispatcher, DT-based CM base mapping, low-level operation registration, and clock provider initialization.

Important APIs/types/functions: Maintains `cm_ll_data`, `cm_base`, and `cm2_base`. Implements `cm_split_idlest_reg()`, module ready/idle waits, module enable/disable, `omap_cm_xlate_clkctrl()`, `cm_register()`, `cm_unregister()`, `omap2_cm_base_init()`, and `omap_cm_init()`. Defines `omap_prcm_init_data` instances and `omap_cm_dt_match_table`.

Control flow: `omap2_cm_base_init()` scans matching DT nodes, ioremaps resources, populates `cm_base`/`cm2_base`, attaches node/memory data, and calls the SoC init hook when enough instances exist. `omap_cm_init()` later initializes clock providers for CM nodes unless flagged `CM_NO_CLOCKS`. Dispatcher functions validate callback presence and call the registered SoC implementation.

State and persistence: Global state includes registered low-level callback pointer and CM base mappings. Mapped MMIO persists for the life of the platform. DT node pointers are stored in init data during setup.

Dependencies: Uses Linux OF/address APIs, `cm2xxx.h`, `cm3xxx.h`, `cm33xx.h`, `cm44xx.h`, and `clock.h`.

Integration points: Central bridge between device tree CM nodes, TI clock providers, CM backends, and hwmod/clock callers.

Risks: `cm_register()` allows only one active low-level implementation, so multi-instance SoCs rely on one backend handling both CM1/CM2 after base setup. Resource mapping errors abort initialization. Missing callbacks produce warnings and `-EINVAL`.

Test signals: Device-tree boot should map the expected compatible nodes, initialize CM backends, and set up clock providers where appropriate. Absence of `WARN_ONCE` dispatcher warnings indicates correct backend registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cminst44xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cminst44xx.c

Purpose: Implements partitioned CM instance access and OMAP4-style clockdomain/module operations for OMAP4, OMAP5, DRA7xx, and AM43xx-style CM layouts.

Important APIs/types/functions: Maintains `_cm_bases[]`, initializes it from PRM/CM1/CM2/PRCM_MPU bases, implements partitioned register read/write/RMW helpers, IDLEST polling, CLKTRCTRL writes, module enable/disable, static dependency add/delete/read/clear, clockdomain sleep/wakeup/allow/deny/clock enable/disable, context save/restore, and `omap4_cm_init()`. Exports `omap4_clkdm_operations` and `am43xx_clkdm_operations`.

Control flow: `omap4_cm_init()` populates `_cm_bases` and registers `omap4xxx_cm_ll_data`. Common CM dispatch uses module operations and xlate. Generic clockdomain dispatch uses operation tables to program CLKSTCTRL or STATICDEP based on `prcm_partition`, `cm_inst`, and `clkdm_offs`.

State and persistence: `_cm_bases[]` stores physical/virtual bases per PRCM partition. Each clockdomain stores saved CLKSTCTRL mode in `clkdm->context`. Hardware CM registers hold active state.

Dependencies: Includes CM1/CM2 OMAP44xx headers, `cm44xx.h`, OMAP34xx regbit mode constants, PRCM/PRM partition headers, and generic clockdomain/CM definitions.

Integration points: Backend for OMAP44xx, OMAP54xx, DRA7xx, and AM43xx clockdomain data. It also services common module enable/disable operations for hwmod on OMAP4-style SoCs.

Risks: Invalid partition or unmapped base triggers BUG_ON. AM43xx uses a reduced operation table without dependency/context callbacks. `omap4_clkdm_save_context()` masks with MODULEMODE/CLKTRCTRL low bits; hardware encoding compatibility is assumed. Static dependency clearing only iterates `wkdep_srcs` for both wake and sleep clear callbacks.

Test signals: OMAP4/5/DRA7/AM43 boot should initialize partition bases before any CM access. Runtime PM should verify module ready/idle timeouts, static dependency bit changes, and suspend/resume context restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cminst44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common-board-devices.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common-board-devices.h

Purpose: Declares legacy common board-device support for OMAP N8x0 Menelaus platform data.

Important APIs/types/functions: Declares `n8x0_legacy_init()` and external `n8x0_menelaus_platform_data`.

Control flow: Header only; board/platform code includes it to initialize legacy N8x0 devices.

State and persistence: No local state. The external Menelaus platform data is defined elsewhere and persists as platform configuration.

Dependencies: Includes `<linux/mfd/menelaus.h>`.

Integration points: Connects OMAP2 board code to legacy Menelaus MFD platform data.

Risks: Legacy board-device interfaces can be configuration-sensitive and are unrelated to DT-centric CM code. Missing Menelaus support would break N8x0 legacy init.

Test signals: Build coverage for N8x0 legacy board configurations and platform device initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common-board-devices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.c

Purpose: Provides small common OMAP2+ machine helpers for early memory reservation.

Important APIs/types/functions: Defines weak `omap_secure_ram_reserve_memblock()` returning 0 by default and `omap_reserve()` calling secure RAM and interconnect barrier reservation helpers.

Control flow: Platform early boot calls `omap_reserve()`, which first reserves secure RAM if a SoC-specific override exists, then reserves interconnect barrier memory when configured.

State and persistence: No local persistent state. Effects are memblock reservations made by called helpers.

Dependencies: Includes `common.h` and `omap-secure.h`; relies on `omap_barrier_reserve_memblock()` declaration and optional override of the weak secure reservation function.

Integration points: Part of OMAP2+ early boot memory reservation path.

Risks: Weak default hides missing secure reservation unless SoC code overrides it. Reservation order can matter for low-level secure firmware/barrier memory needs.

Test signals: Boot logs and memblock layout on secure-enabled OMAP platforms; builds with and without interconnect barrier support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.h

Purpose: Aggregates common OMAP2+ machine declarations, configuration-dependent stubs, early/late init hooks, PM hooks, restart hooks, MMIO mapping hooks, low-level SMP/CPU idle helpers, and the `omap_test_timeout()` polling macro.

Important APIs/types/functions: Declares PM init functions, L2 cache helpers, SoC early/late init functions, restart functions, barrier reservation/init, map_io functions, GIC helpers, SCU/L2/SAR/MPUSS helpers, SMP ops, low-power CPU entry functions, auxdata/PCS legacy hooks, SDRC init, `omap_reserve()`, DSS reset, clock init, and IOMMU powerdomain constraints. Defines `OMAP_INTC_START`, `OMAP_L2C_AUX_CTRL`, and `omap_test_timeout()`.

Control flow: Header only. Many declarations are selected by Kconfig with inline no-op fallbacks, allowing common call sites to compile across SoCs. `omap_test_timeout()` expands into a microsecond polling loop used by CM backends.

State and persistence: No direct state, but declares many platform state providers and low-power entry functions. The timeout macro is stack-local at call sites.

Dependencies: Linux IRQ, delay, I2C, TWL, reboot, OMAP INTC, ARM cache/proc headers, and local I2C/platform declarations.

Integration points: Broad OMAP2+ platform integration header used across init, PM, SMP, cache, device, clock, and reset code. In this subset, CM backends depend on `omap_test_timeout()`.

Risks: Because it exposes many conditional no-op stubs, build success does not guarantee runtime feature availability. Timeout polling is busy-wait based and depends on correct timeout values and `udelay()`.

Test signals: Multi-SoC build matrix, boot through early/late init, restart, suspend/resume, SMP bringup, and CM wait loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.h -->
