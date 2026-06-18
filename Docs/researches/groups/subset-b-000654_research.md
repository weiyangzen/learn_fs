# subset-b-000654 Research

Grouped research for the listed OMAP2 PRCM/PRM/SDRC/suspend files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm-common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm-common.h

## Purpose
Defines PRCM module offsets, shared PRM/CM bit masks, common timeout helpers, PRCM interrupt metadata, and PRCM init-data structures used across OMAP2/3/4-era ARM SoCs. It is the shared vocabulary that lets SoC-specific PRM, CM, wakeup, and device-tree init code refer to hardware registers consistently.

## APIs, Flow, And State
The file is mostly declarative macros for module offsets and bitfields: OCP/MPU/CORE/GFX/WKUP/PLL plus OMAP24xx, OMAP3430, TI81xx, enable/status/wakeup bits, IO-chain masks, and dependency bits. Runtime-facing APIs include `omap_test_timeout(cond, timeout, index)`, `struct omap_prcm_irq`, `struct omap_prcm_irq_setup`, `OMAP_PRCM_IRQ`, `struct omap_domain_base`, and `struct omap_prcm_init_data`. The PRCM IRQ setup structure carries hardware register offsets, callback hooks, saved IRQ masks, priority masks, base IRQ allocation, and suspend flags that are populated by `prm_common.c`.

## Dependencies And Integration
Included by almost every file in this set. Depends on Linux delay APIs outside assembly and on `bool`, `u*`, `s*`, `__iomem`, and device-tree types via the including context. Its data structures connect SoC PRM implementations to the common chained IRQ code and to `omap2_prm_base_init()` discovery.

## Risks And Test Signals
Incorrect bit masks or offsets can break low-level clock, reset, wakeup, or power-domain transitions across many SoCs. The duplicated `OMAP3430_EN_GPT12` define and comments about possible TI documentation bugs are maintenance hazards. Test signals are boot on affected SoCs, PRCM IRQ delivery, suspend/resume with IO wakeups, reset-source reporting, and successful powerdomain transitions without timeout warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm43xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm43xx.h

## Purpose
Provides AM43xx PRCM partition, PRM instance, CM instance, clockdomain offset, interrupt register, IO power-control, and selected clock-control register offsets.

## APIs, Flow, And State
This header exposes macros only. Key constants include `AM43XX_PRM_PARTITION`, `AM43XX_CM_PARTITION`, `AM43XX_PRM_*_INST`, `AM43XX_PRM_IRQSTATUS_MPU_OFFSET`, `AM43XX_PRM_IRQENABLE_MPU_OFFSET`, `AM43XX_PRM_IO_PMCTRL_OFFSET`, `AM43XX_CM_*_INST`, clockdomain offsets such as `AM43XX_CM_PER_EMIF_CDOFFS`, and `AM43XX_CM_PER_EMIF_CLKCTRL_OFFSET`. No runtime state is stored here.

## Dependencies And Integration
Consumed by `prm44xx.c`, `sleep43xx.S`, PRM/CM register accessors, and AM43xx-specific initialization that reuses the OMAP4-style PRM code with AM43xx offsets. It integrates with device-tree compatible `ti,am4-prcm`.

## Risks And Test Signals
The AM43xx reuse of OMAP4-style code makes offset accuracy critical; a wrong IRQ or IO PMCTRL offset breaks chained PRCM IRQs and wakeups. Test signals include AM43xx boot, PRM IRQ setup with a single IRQ register, EMIF clock control during suspend, and RTC+DDR wake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm43xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm44xx.h

## Purpose
Defines PRCM partition IDs for OMAP4, OMAP5, and DRA7xx register spaces. These IDs select between PRM, CM, SCRM, and local MPU PRCM base mappings.

## APIs, Flow, And State
The file exports partition constants such as `OMAP4430_PRM_PARTITION`, `OMAP4430_CM1_PARTITION`, `OMAP4430_PRCM_MPU_PARTITION`, `OMAP54XX_CM_CORE_PARTITION`, and `DRA7XX_MPU_PRCM_PARTITION`. `OMAP4_MAX_PRCM_PARTITIONS` sizes the partition base array in `prminst44xx.c`. There is no executable flow or stored state.

## Dependencies And Integration
Used by `prminst44xx.c`, `prm44xx.c`, OMAP4/5/DRA register headers, and PRCM MPU accessors. The partition values index `_prm_bases[]` and therefore are part of the ABI between generated register data and low-level accessors.

## Risks And Test Signals
Partition IDs are described as arbitrary but must remain stable with the array sizing and invalid partition convention. Bad IDs cause BUG_ON failures or register writes to the wrong PRCM block. Test signals are OMAP4/5/DRA PRM access, hardreset operations, and VP/VC register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.c

## Purpose
Implements the minimal OMAP4 PRCM_MPU register accessor layer and stores the local MPU PRCM base address for early code.

## APIs, Flow, And State
Exports `struct omap_domain_base prcm_mpu_base`, `omap4_prcm_mpu_read_inst_reg(inst, reg)`, `omap4_prcm_mpu_write_inst_reg(val, inst, reg)`, and `omap2_set_globals_prcm_mpu(prcm_mpu)`. Reads and writes use relaxed MMIO through `OMAP44XX_PRCM_MPU_REGADDR`. State is the global `prcm_mpu_base.va`, populated during early platform setup and later copied into the partition table by `omap_prm_base_init()`.

## Dependencies And Integration
Includes PRCM MPU register definitions and CM register bits. Used by PRM instance code to expose the PRCM_MPU partition beside the global PRM partition, enabling CPU-local power/reset/clock registers to be accessed through the common PRM instance path.

## Risks And Test Signals
The base setter is marked transitional; if not called or mapped before use, local MPU PRCM access fails. Test signals include successful CPU power state reads/writes, CPU reset context access, and OMAP4 suspend paths that touch PRCM_MPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.h

## Purpose
Declares OMAP44xx PRCM_MPU base address, instance offsets, clockdomain offsets, and CPU0/CPU1 register offsets for the local MPU PRCM block.

## APIs, Flow, And State
The key accessor macro is `OMAP44XX_PRCM_MPU_REGADDR(inst, reg)`, based on `OMAP4430_PRCM_MPU_BASE`. Constants identify OCP socket, device PRM, CPU0, and CPU1 instances plus registers such as `PM_CPUx_PWRSTCTRL`, `PM_CPUx_PWRSTST`, `RM_CPUx_CPUx_CONTEXT`, reset control/status, and clock control/status. It contains no state beyond generated address constants.

## Dependencies And Integration
Includes the shared PRCM MPU prototype header. Used by `prcm_mpu44xx.c`, SMP/PM code, and partitioned PRM access. It aligns OMAP4 CPU-local register layout with generated hwmod/clock/powerdomain data.

## Risks And Test Signals
Register offsets are generated hardware data; manual drift can break CPU idle, reset, or context-loss accounting. Test signals are CPU0/CPU1 low-power entry, hotplug/suspend behavior, and access to PRCM_MPU context registers without faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu54xx.h

## Purpose
Defines OMAP54xx local MPU PRCM base, instance offsets, clockdomain offsets, and CPU0/CPU1 power/reset/clock register offsets.

## APIs, Flow, And State
The primary macro is `OMAP54XX_PRCM_MPU_REGADDR(inst, reg)`. Instances are split into OCP socket, device, PRM_C0/CM_C0, and PRM_C1/CM_C1. The header provides offsets for revision, reset status, fractional incrementer registers, CPU power state control/status, CPU reset control/status/context, clock state control, and `CM_CPUx_CPUx_CLKCTRL`. No mutable state is stored.

## Dependencies And Integration
Includes `prcm_mpu_44xx_54xx.h` and `common.h`; used by OMAP5 PRCM MPU consumers and by generated clock/powerdomain tables. It mirrors the OMAP4 programming model but with OMAP5 instance splits.

## Risks And Test Signals
The OMAP5 CPU PRM/CM split means cross-porting OMAP4 offsets directly would be unsafe. Test signals are OMAP5 CPU idle/resume, clockdomain control for CPU0/CPU1, and reset/context register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu7xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu7xx.h

## Purpose
Provides DRA7xx MPU_PRCM base, instance offsets, clockdomain offsets, and CPU-local power/reset/clock register offsets.

## APIs, Flow, And State
The `DRA7XX_PRCM_MPU_REGADDR(inst, reg)` macro maps MPU_PRCM physical addresses into L4 IO space. Instances cover OCP socket, device, PRM/CM for CPU0 and CPU1. Register offsets include revision, fractional incrementer numerator/denominator, CPU power state, reset control/status, context, clock state control, and CPU clock control. It is declarative only.

## Dependencies And Integration
Includes the shared 44xx/54xx PRCM MPU prototypes. The definitions are consumed by DRA7xx platform PM and clock code that shares the OMAP4+ register-access model.

## Risks And Test Signals
As generated data, the principal risk is stale DRA7xx offsets or naming mismatches in call sites. Test signals are DRA7xx CPU idle, SMP suspend/resume, and PRCM MPU MMIO access without BUGs or bus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu7xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu_44xx_54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu_44xx_54xx.h

## Purpose
Declares common PRCM_MPU access functions and the global PRCM_MPU base for OMAP44xx/54xx-style local MPU PRCM blocks.

## APIs, Flow, And State
Exports `prcm_mpu_base`, `omap4_prcm_mpu_read_inst_reg()`, `omap4_prcm_mpu_write_inst_reg()`, and `omap2_set_globals_prcm_mpu()`. These APIs abstract instance/register MMIO access while SoC-specific headers supply concrete offsets.

## Dependencies And Integration
Includes `prcm-common.h` outside assembly. Used by OMAP44xx, OMAP54xx, and DRA7xx PRCM MPU headers and implementation. It feeds `prminst44xx.c` partition setup through the shared `prcm_mpu_base`.

## Risks And Test Signals
The shared names are OMAP4-prefixed even when used by later SoCs, which can obscure SoC-specific register-layout differences. Test signals are compile coverage across OMAP4/5/DRA configs and successful local MPU PRCM register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu_44xx_54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-24xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-24xx.h

## Purpose
Defines OMAP24xx PRM-specific bit shifts and masks for power state forcing, autoidle, external voltage control, clock output, emulation, wake dependencies, and reset sources.

## APIs, Flow, And State
This is a macro-only register bit header. Notable constants include `OMAP24XX_FORCESTATE_MASK`, `OMAP24XX_AUTOIDLE_MASK`, voltage level setup shifts, `OMAP2420_CLKOUT2_*`, `OMAP24XX_CLKOUT_*`, wake dependency bits for MPU-to-MDM/DSP, and reset source shifts used by `prm2xxx.c`.

## Dependencies And Integration
Includes `prm2xxx.h` and is consumed by OMAP2 PRM implementation, clockdomain sleep/wakeup control, and reset-source mapping.

## Risks And Test Signals
OMAP2 uses reversed power state encodings compared with later OMAP generations, so these constants must be paired with the conversion code in `prm2xxx.c`. Test signals are OMAP24xx idle, wake dependency behavior, clock output setup, and reset source reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-24xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-33xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-33xx.h

## Purpose
Defines AM33xx PRM bit masks for powerdomain memory state, logic retention/status, low-power state requests, reset control, and previous power-state tracking.

## APIs, Flow, And State
Macro-only definitions cover GFX, PRUSS, MPU L1/L2/RAM, PER memory, RAM memory, `AM33XX_LOWPOWERSTATECHANGE`, `AM33XX_LASTPOWERSTATEENTERED`, logic retention/status, and global warm/cold reset bits. No executable state.

## Dependencies And Integration
Includes `prm.h` and is consumed by `prm33xx.c` powerdomain operations and AM33xx reset code. The masks map `struct powerdomain` mask arrays to actual PRM registers.

## Risks And Test Signals
Bank-specific masks are used through generic powerdomain callbacks; an incorrect mask can silently program the wrong retention/on state. Test signals are AM33xx suspend/resume, powerdomain previous-state reads, and warm/cold reboot mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-33xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-34xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-34xx.h

## Purpose
Defines OMAP3430/3630 PRM bitfields for voltage controller/processor registers, wake group selection, reset causes, IO-chain control, power state memory banks, SmartReflex, and clock/voltage setup.

## APIs, Flow, And State
This header is declarative. It includes masks for VP config/status (`VPENABLE`, `FORCEUPDATE`, `VPx_TRANXDONE`), voltage controller I2C fields, wake group-select masks for GPIO/UART/GPT/MCBSP/DSS/IVA2, IVA reset bits, memory state masks, IO wake/chain bits, reset source shifts, and voltage control/polarity masks.

## Dependencies And Integration
Includes `prm3xxx.h` and is central to `prm3xxx.c`, OMAP3 PM init, IO wake chain reconfiguration, VP transaction completion, and reset-source translation.

## Risks And Test Signals
This file mixes OMAP3430, OMAP3630, and ES-specific fields; using the wrong revision mask can break wakeups or USB/SmartReflex behavior. Test signals are OMAP3 PM init, IO wake interrupts, SmartReflex VP transactions, reset-source reporting, and off-mode restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-34xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-44xx.h

## Purpose
Defines OMAP44xx PRM bit masks and shifts for reset sources, voltage controller/processor, IO wake clock control, context loss, memory/logic states, and global wake enable.

## APIs, Flow, And State
Macro-only definitions include reset source shifts (`GLOBAL_COLD`, `GLOBAL_WARM_SW`, `MPU_WDT`, `C2C`), VC command/voltage fields, VP transaction done masks for MPU/IVA/CORE, `OMAP4430_GLOBAL_WUEN_MASK`, `OMAP4430_WUCLK_*`, power-state and memory-state masks, and context-loss masks.

## Dependencies And Integration
Consumed by `prm44xx.c`, `prminst44xx.c`, and OMAP4+ voltage/powerdomain code. The reset-source map and IO-chain routines directly depend on these constants.

## Risks And Test Signals
Voltage and wake bits affect hardware-level power sequencing; wrong masks can hang suspend/resume or misreport reset causes. Test signals are OMAP4 PRCM IRQs, IO wake chain reconfiguration, VP transaction completion, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm.h

## Purpose
Defines the common OMAP2+ PRM interface, feature flags, timeout constants, standardized reset-source IDs, and the `prm_ll_data` callback table used to dispatch generic PRM operations to SoC-specific implementations.

## APIs, Flow, And State
Exports global state `prm_base`, `prm_features`, and `prm_reboot_mode`, plus init APIs `omap_prcm_init()` and `omap2_prcm_base_init()`. The `struct prm_reset_src_map` translates hardware reset bits to standardized reset-source bits. `struct prm_ll_data` contains callbacks for reset source reads, context-loss handling, late init, hardreset control, system reset, wake IRQ clearing, and VP transaction completion. Generic wrappers include `omap_prm_assert_hardreset()`, `omap_prm_deassert_hardreset()`, `omap_prm_reset_system()`, `omap_prm_clear_mod_irqs()`, and VP helpers.

## Dependencies And Integration
Includes `prcm-common.h`; implemented primarily by `prm_common.c` and populated by `prm2xxx.c`, `prm3xxx.c`, `prm33xx.c`, and `prm44xx.c`. Used by hwmod, powerdomain, clockdomain, voltage, watchdog, and platform reboot paths.

## Risks And Test Signals
This is a low-level dispatch interface with weak runtime checking: missing callbacks produce warnings or `-EINVAL`, and reset paths may not return. Test signals are callback registration ordering, hardreset deassert timeout behavior, watchdog reset-source reads, and platform reboot modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.c

## Purpose
Implements OMAP2xxx-specific PRM operations: reset-source mapping, DPLL reset reboot, wake status clearing, clockdomain sleep/wakeup, and OMAP2 powerdomain operation callbacks.

## APIs, Flow, And State
Key exported functions are `omap2xxx_clkdm_sleep()`, `omap2xxx_clkdm_wakeup()`, and `omap2xxx_prm_init()`. Static flow maps `PRM_RSTST_WKUP` bits to standard reset IDs, converts OMAP24xx reversed power-state encodings to common `PWRDM_POWER_*` values, toggles `OMAP_RST_DPLL3_MASK` for reboot, and clears module wake status by writing back masked `PM_WKST` bits. `omap2_pwrdm_operations` binds set/read next/current power state, memory state operations from the shared OMAP2/3 file, and transition waits.

## Dependencies And Integration
Depends on `powerdomain`, `clockdomain`, `prm2xxx.h`, `cm2xxx_3xxx.h`, and OMAP24xx bit definitions. Registers its `prm_ll_data` with `prm_register()`, supplying hardreset callbacks from `prm2xxx_3xxx.c`.

## Risks And Test Signals
OMAP2 power-state encodings differ from OMAP3+, making conversion correctness important. DPLL reset and wake-status clear code writes hardware directly. Test signals are OMAP2 clockdomain sleep/wakeup, powerdomain state reads, reboot through DPLL reset, and accurate reset-source bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.h

## Purpose
Declares OMAP2xxx PRM register address macros, global PRCM register offsets, module-specific PRM offsets, OMAP24xx-specific wake/IRQ offsets, and OMAP2 PRM init/clockdomain APIs.

## APIs, Flow, And State
Address macros `OMAP2420_PRM_REGADDR()` and `OMAP2430_PRM_REGADDR()` generate MMIO addresses. The header provides revision/sysconfig/IRQ/voltage/clock source/clock output/voltage setup/polarity offsets, common module registers (`RM_RSTCTRL`, `RM_RSTST`, `PM_PWSTCTRL`, `PM_WKEN`, `PM_WKST`, `PM_WKDEP`), and OMAP24xx second wake registers. It declares `omap2xxx_clkdm_sleep()`, `omap2xxx_clkdm_wakeup()`, and `omap2xxx_prm_init()`.

## Dependencies And Integration
Includes `prcm-common.h`, `prm.h`, and `prm2xxx_3xxx.h`. Used by OMAP2 PRM implementation, assembly/SDRC code, and clockdomain code.

## Risks And Test Signals
The same offset names are shared with OMAP3 but some OMAP2 global registers carry PRCM names, so call sites must use the right base/register accessor. Test signals are OMAP2420/2430 boot, PRCM IRQ access, voltage setup writes, and reset/wakeup register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.c

## Purpose
Implements PRM functionality shared by OMAP2 and OMAP3: submodule hardreset operations, common powerdomain memory/logic operations, powerdomain transition polling, and clockdomain wake dependency manipulation.

## APIs, Flow, And State
Exports `omap2_prm_is_hardreset_asserted()`, `omap2_prm_assert_hardreset()`, and `omap2_prm_deassert_hardreset()`. Deassert flow checks for already-deasserted reset, clears status by writing one, clears the reset control bit, then uses `omap_test_timeout()` against `RM_RSTST`. Powerdomain functions set/read memory on/retention/status masks and logic retention through PRM RMW helpers. `omap2_pwrdm_wait_transition()` polls `OMAP_INTRANSITION_MASK`. Clockdomain dependency helpers set, clear, read, and bulk-clear `PM_WKDEP` bits while updating dependency usecounts.

## Dependencies And Integration
Depends on `powerdomain`, `clockdomain`, `prm2xxx_3xxx.h`, and OMAP24xx register bits. It is reused by OMAP2 and OMAP3 PRM low-level data tables and powerdomain operation tables.

## Risks And Test Signals
Hardreset deassert sequencing is timing-sensitive and can return `-EEXIST` or `-EBUSY`; callers must handle these outcomes. Clockdomain bulk clear assumes caller holds the powerdomain lock. Test signals are hwmod reset/deassert operations, powerdomain transition latency, wake dependency changes, and no timeout logs under suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.h

## Purpose
Provides shared OMAP2/3 PRM register offsets, inline module register accessors, common hardreset/powerdomain/clockdomain prototypes, and shared PRM bit masks.

## APIs, Flow, And State
Inline APIs read, write, RMW, set, clear, and read-shift PRM module registers via `prm_base.va + module + idx`. Prototypes cover hardreset, memory state, logic retention, transition polling, and wake dependency operations. Shared register fields include event generator timings, clock setup/source fields, reset timing/control/status bits, wake dependency bits, and logic retention.

## Dependencies And Integration
Includes `prcm-common.h`, `prm.h`, Linux IO, and `powerdomain.h`. It is the common include for `prm2xxx.c`, `prm3xxx.c`, and many OMAP2/3 power/clock call sites.

## Risks And Test Signals
Inline relaxed MMIO helpers assume `prm_base.va` is initialized and callers provide locking where noted. `__ffs(mask)` requires nonzero masks. Test signals include successful OMAP2/3 PRM MMIO after DT base init, hardreset operations, and powerdomain memory-bank reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.c

## Purpose
Implements AM33xx PRM operations for register access, hardreset control, powerdomain callbacks, reboot, and powerdomain context save/restore.

## APIs, Flow, And State
Static accessors read/write/RMW `prm_base.va + inst + idx`. Hardreset functions mirror OMAP4-style sequencing: test reset bit, clear status, deassert control, then poll status with `MAX_MODULE_HARDRESET_WAIT`. Powerdomain operations set/read next/current power state, request low-power state changes, clear previous state, set/read logic retention and memory bank states using per-domain masks, and poll `OMAP_INTRANSITION_MASK`. `am33xx_prm_global_sw_reset()` selects warm reset by default and cold reset when `prm_reboot_mode == REBOOT_COLD`. Context persistence is stored in `pwrdm->context`, with `LOWPOWERSTATECHANGE` masked out before restore.

## Dependencies And Integration
Depends on `powerdomain`, `prm33xx.h`, and AM33xx bit definitions. Registers `am33xx_prm_ll_data` with common PRM code and exposes `am33xx_pwrdm_operations` to the powerdomain layer. Integrates with Linux reboot modes.

## Risks And Test Signals
Array-indexed powerdomain masks must be valid for the requested memory bank. Context restore compares current state and saved control state before waiting, so incorrect offsets can cause missed waits or hangs. Test signals are AM33xx suspend/resume, RTC/DDR modes, hardreset users, and cold-vs-warm reboot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.h

## Purpose
Declares AM33xx PRM base address, register address macro, PRM instance offsets, key power/reset register offsets, and PRM init prototype.

## APIs, Flow, And State
`AM33XX_PRM_REGADDR(inst, reg)` maps PRM addresses through the AM33xx L4 wakeup IO window. Instance macros cover OCP socket, PER, WKUP, MPU, DEVICE, RTC, GFX, and CEFUSE. Register offsets include power state control/status for PER/WKUP/MPU/RTC/GFX/CEFUSE and device reset control. Declares `am33xx_prm_init()`.

## Dependencies And Integration
Includes `prcm-common.h` and `prm.h`. Used by AM33xx PRM implementation, clock/powerdomain tables, and assembly suspend code that references related CM/PRM layout.

## Risks And Test Signals
The header has both offset and resolved-address macros; call sites must choose register-offset macros for instance accessors and resolved addresses only for direct MMIO. Test signals are AM33xx PRM initialization, powerdomain callbacks, and reset control access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.c

## Purpose
Implements OMAP3 PRM support: reset-source mapping, voltage controller/processor access, PRCM IRQ setup, IO wake chain reconfiguration, PM register initialization, IVA idling, powerdomain operations, and late IO-wakeup IRQ registration.

## APIs, Flow, And State
Exports `omap3_prm_vcvp_read/write/rmw()`, `omap3xxx_prm_init()`, `omap3xxx_prm_clear_global_cold_reset()`, `omap3_prm_save_scratchpad_contents()`, and `omap3_prm_init_pm()`. Static flow maps reset status to standard reset IDs, checks/clears VP TXDONE bits, performs DPLL3 reset for reboot, reads pending PRM IRQs as enabled-and-status bits, saves/restores IRQ masks for suspend, and clears module wake IRQs by temporarily enabling clocks until wake bits clear. PM init programs wake enables/group selects, clears reset flags, idles IVA2, and resets the modem block. IO-chain paths differ for pre-ES3.1 and later hardware. `omap3_pwrdm_operations` adds previous-state reads, hardware SAR, and OMAP3-specific memory previous-state mapping.

## Dependencies And Integration
Depends on SoC feature detection, VP/voltage code, powerdomain/clockdomain, OMAP2/3 PRM/CM access, OMAP3 register bits, and device tree IRQ lookup for `ti,omap3-prm`. Registers `omap3xxx_prm_ll_data` and optionally a chained PRCM IRQ handler.

## Risks And Test Signals
Wake status clearing manipulates module clocks and has USBHOST special handling; mistakes can lose wake events or alter clock state. IO-chain timing can warn on latch timeout. IVA idling touches an accelerator that may be absent but clock-active. Test signals are OMAP3 off-mode, IO wake interrupt delivery, VP transaction completion, DSS low-power retention, reset-source reads, and absence of `powerdomain waited too long` logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.h

## Purpose
Declares OMAP3 PRM address macros, global PRM/VC/VP/reset/clock/voltage register offsets, OMAP3-specific module offsets, and OMAP3 PRM public APIs.

## APIs, Flow, And State
`OMAP34XX_PRM_REGADDR(module, reg)` maps PRM addresses. Register constants cover revision/sysconfig/IRQ status/enable, VC SMPS address/voltage/command/bypass/config, VP1/VP2 config/status/limits/voltage/steps, reset, voltage control, clock source/setup/polarity, and clock output. OMAP3-specific offsets include wake/status/group-select registers and IVA IRQs. APIs declare VC/VP accessors, PRM init, global cold-reset clear, scratchpad save, and PM init.

## Dependencies And Integration
Includes `prcm-common.h`, `prm.h`, and `prm2xxx_3xxx.h`. Used by OMAP3 PRM, voltage, PM, and low-level suspend code.

## Risks And Test Signals
The header handles OMAP3 global registers split across GR and CCR modules; wrong module selection changes the target physical register. Test signals are OMAP3 PRM base access, voltage controller register programming, IRQ offsets, and suspend scratchpad restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.c

## Purpose
Implements OMAP4/OMAP5/DRA7/AM43xx-style PRM support: PRM MMIO access, VP/VC access, chained PRCM IRQ support, IO wake chain control, reset-source mapping, context-loss helpers, powerdomain operations, AM43xx context save/restore, and PRM registration.

## APIs, Flow, And State
Exports `omap4_prm_vcvp_read/write/rmw()` and `omap44xx_prm_init()`. Static state includes `omap4_prcm_irq_setup`, `omap_prm_context`, and `prm_init_data`. IRQ flow reads each IRQENABLE/IRQSTATUS pair, saves and clears masks during suspend, restores them on resume, and uses IO event priority. IO-chain reconfiguration toggles `WUCLK_CTRL` and waits for `WUCLK_STATUS` assertion/deassertion. Reset-source flow reads the device PRM reset status and maps bits to standard IDs. Powerdomain operations use partitioned `omap4_prminst_*` accessors for next/current/previous power state, logic/memory retention, low-power state changes, transition polling, and context save/restore. AM43xx can save PRM IRQ enable and IO PMCTRL around CPU cluster PM when off mode is enabled.

## Dependencies And Integration
Depends on CPU PM, device-tree IRQ lookup, SoC detection, VP/voltage, PRM instance access, OMAP4/AM43xx register bits, `powerdomain`, and `pm.h` off-mode state. Registers `omap44xx_prm_ll_data` and late-registers the chained IO wake IRQ when `PRM_HAS_IO_WAKEUP` is present.

## Risks And Test Signals
This code adapts multiple SoC families; AM43xx changes IRQ register count and offsets at init time. `prm_restore_context()` mixes OMAP4 and AM43xx instance constants, so context save/restore is tightly coupled to compatible selection. Test signals are OMAP4/5/DRA/AM43xx boot, IO wake interrupts, VP TXDONE handling, powerdomain context restore, AM43xx RTC-DDR/off-mode resume, and reset-source reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.h

## Purpose
Declares OMAP44xx PRM base address, PRM instance offsets, clockdomain offsets, common OMAP4 power/reset register offsets, IRQ register offsets, device PRM voltage/IO/VP/VC offsets, and address macros.

## APIs, Flow, And State
`OMAP44XX_PRM_REGADDR(inst, reg)` maps OMAP4 PRM addresses. Instance macros cover OCP socket, CKGEN, MPU, TESLA, ABE, ALWAYS_ON, CORE, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, CEFUSE, WKUP, EMU, and DEVICE. Register constants include `OMAP4_PM_PWSTCTRL`, `OMAP4_PM_PWSTST`, IRQSTATUS/IRQENABLE, MPU context, reset control, IO PMCTRL, voltage setup, VP configs/status, VC SMPS/command/bypass/channel/I2C config.

## Dependencies And Integration
Includes shared OMAP4/5 PRM prototypes and `prm.h`. Used by `prm44xx.c`, `prminst44xx.c`, voltage code, powerdomain data, and generated clockdomain tables.

## Risks And Test Signals
Because many offsets are reused by generic `omap44xx_prm_init()`, offset mistakes affect several independent features. Test signals are OMAP4 PRM IRQ, voltage controller setup, powerdomain read/write, and hardreset operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx_54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx_54xx.h

## Purpose
Declares the common OMAP4/OMAP5 PRM voltage controller/processor accessor APIs and PRM init function.

## APIs, Flow, And State
Exports `omap4_prm_vcvp_read(offset)`, `omap4_prm_vcvp_write(val, offset)`, `omap4_prm_vcvp_rmw(mask, bits, offset)`, and `omap44xx_prm_init(data)`. The implementation dynamically selects the device PRM instance through `omap4_prmst_get_prm_dev_inst()`.

## Dependencies And Integration
Includes `prcm-common.h`. Used by OMAP44xx and OMAP54xx PRM register headers and voltage/PM code that shares the OMAP4-style PRM programming model.

## Risks And Test Signals
The function names are OMAP4-prefixed but used for later SoCs; correctness depends on `device_inst_offset` in init data. Test signals are VP/VC register access on OMAP4 and OMAP5 and successful `omap44xx_prm_init()` registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx_54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm54xx.h

## Purpose
Defines OMAP54xx PRM base address, PRM instance offsets, clockdomain offsets, and selected device PRM voltage setup offsets.

## APIs, Flow, And State
The `OMAP54XX_PRM_REGADDR(inst, reg)` macro maps OMAP5 PRM MMIO. Instance offsets include OCP socket, CKGEN, MPU, DSP, ABE, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, CUSTEFUSE, WKUPAON, EMU, and DEVICE. Device PRM voltage setup offsets cover CORE/MPU/MM retention sleep. No executable flow or state.

## Dependencies And Integration
Includes shared OMAP4/5 PRM prototypes and `prm.h`. Used by common `omap44xx_prm_init()` through OMAP5 init data with `OMAP54XX_PRM_DEVICE_INST`.

## Risks And Test Signals
OMAP5 uses the OMAP4-style common PRM implementation but different instance layout and base address. Test signals are OMAP5 PRM init, voltage retention setup, powerdomain register access, and wake/reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm7xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm7xx.h

## Purpose
Defines DRA7xx PRM base address, PRM instance offsets, clockdomain offsets, and a CKGEN system clock select address.

## APIs, Flow, And State
`DRA7XX_PRM_REGADDR(inst, reg)` maps DRA7xx PRM registers. Instance offsets cover MPU, DSP1/DSP2, IPU, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, L4PER, CUSTEFUSE, WKUPAON, EMU, EVE1-4, RTC, VPE, and DEVICE. `DRA7XX_CM_CLKSEL_SYS` exposes a CKGEN register address. This header is declarative.

## Dependencies And Integration
Includes `prcm-common.h`, shared OMAP4/5 PRM declarations, and `prm.h`. Used by DRA7xx PRM init data and PRM instance access.

## Risks And Test Signals
DRA7xx has many accelerator instances, so offset drift impacts hardreset/power management for DSP/IPU/EVE/IVA/GPU domains. Test signals are DRA7xx boot, device reset control, powerdomain transitions, and system clock select access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm7xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm_common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm_common.c

## Purpose
Provides the common OMAP2+ PRM core: global PRM base/features, chained PRCM interrupt controller setup, suspend-aware PRCM IRQ masking, generic wrappers around SoC-specific `prm_ll_data`, device-tree PRM base discovery, clock provider setup, and late PRM initialization.

## APIs, Flow, And State
Public APIs include `omap_prcm_event_to_irq()`, `omap_prcm_irq_prepare()`, `omap_prcm_irq_complete()`, `omap_prcm_register_chain_handler()`, hardreset wrappers, context-loss wrappers, `omap_prm_reset_system()`, `omap_prm_clear_mod_irqs()`, VP helpers, `prm_register()`, `prm_unregister()`, `omap2_prcm_base_init()`, and `omap_prcm_init()`. State includes `prm_base`, `prm_features`, `prm_reboot_mode`, `prm_ll_data`, `prcm_irq_setup`, and allocated generic IRQ chip/mask arrays. IRQ flow masks at PRM level when suspended, repeatedly reads pending events, dispatches priority events first, acknowledges/EOIs/unmasks the parent IRQ, then performs an OCP barrier. Base init scans DT compatibles, ioremaps PRM/SCRM/PLLSS blocks, sets `prm_base`, calls SoC init hooks, then initializes CM bases and clock providers.

## Dependencies And Integration
Depends on Linux IRQ, OF address, clock provider, TI clock, PRM/CM/SCRM headers, control/PCS legacy setup, and SoC-specific PRM init data. It is the integration point between platform device tree nodes, clock infrastructure, powerdomain/hwmod reset wrappers, and PRCM wake IRQ handling.

## Risks And Test Signals
`OMAP_PRCM_MAX_NR_PENDING_REG` caps chained IRQ handling at two status registers. Registration rejects duplicate setup, and error cleanup must handle partially initialized IRQ chips. `omap_prm_reset_system()` spins forever after reset request. Test signals are DT PRM node discovery, IRQ descriptor allocation, `omap_prcm_event_to_irq("io")`, suspend/resume mask save/restore, PRM wrapper warnings, and subsystem late init success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.c

## Purpose
Implements partitioned PRM instance access for OMAP4-style PRM blocks, including PRM/PRCM_MPU base table population, device PRM instance selection, hardreset operations, and global warm reset.

## APIs, Flow, And State
State includes `_prm_bases[OMAP4_MAX_PRCM_PARTITIONS]` and `prm_dev_inst`. `omap_prm_base_init()` copies global PRM and PRCM_MPU bases into the partition array. `omap4_prmst_get_prm_dev_inst()` and `omap4_prminst_set_prm_dev_inst()` manage the device instance used by VP/VC and reset code. Register APIs read, write, and RMW `base + inst + idx`, with BUG_ON validation for invalid partition or missing mapping. Hardreset deassert clears status, clears reset control, and polls status via `omap_test_timeout()`. `omap4_prminst_global_warm_sw_reset()` sets `OMAP4430_RST_GLOBAL_WARM_SW_MASK` and reads back as an OCP barrier.

## Dependencies And Integration
Depends on PRM/PRCM MPU headers, partition IDs, OMAP4 reset bits, and SoC detection headers. Used by `prm44xx.c`, hwmod reset paths, VP/VC accessors, and platform reboot.

## Risks And Test Signals
BUG_ONs make missing base initialization fatal rather than recoverable. `prm_dev_inst` must be set before device-level accesses. Test signals are OMAP4+ hardreset assert/deassert, PRM reset control, partitioned reads for PRM and PRCM_MPU, and global warm reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.h

## Purpose
Declares OMAP4-style PRM instance accessors, device instance controls, hardreset helpers, global warm reset, and partition base initialization.

## APIs, Flow, And State
Defines `PRM_INSTANCE_UNKNOWN` and exposes `omap4_prmst_get_prm_dev_inst()`, `omap4_prminst_set_prm_dev_inst()`, `omap4_prminst_read_inst_reg()`, `omap4_prminst_write_inst_reg()`, `omap4_prminst_rmw_inst_reg_bits()`, `omap4_prminst_global_warm_sw_reset()`, hardreset assert/deassert/status APIs, and `omap_prm_base_init()`.

## Dependencies And Integration
Consumed by `prm44xx.c`, `prminst44xx.c`, voltage code, and OMAP4+ hwmod/powerdomain code. It is the public surface for partition-aware PRM access.

## Risks And Test Signals
The header intentionally exports low-level functions despite comments that this is not ideal, increasing the chance of direct register access bypassing higher-level locking or SoC checks. Test signals are compile coverage for OMAP4+ configs and hardreset/powerdomain users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/scrm44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/scrm44xx.h

## Purpose
Defines OMAP44xx SCRM base address, register address macro, and CLKSETUPTIME fields.

## APIs, Flow, And State
`OMAP44XX_SCRM_REGADDR(reg)` maps SCRM registers. The header exposes `OMAP4_SCRM_CLKSETUPTIME` and its `DOWNTIME` and `SETUPTIME` masks/shifts. There is no runtime state.

## Dependencies And Integration
Used by PRCM/clock setup code through SCRM DT nodes and TI clock provider initialization. It complements PRM/CM register headers for OMAP4/5 SCRM partitions.

## Risks And Test Signals
Incorrect setup/downtime fields can affect system clock setup timing around low-power transitions. Test signals are clock provider initialization for `ti,omap4-scrm`/`ti,omap5-scrm` and stable suspend/resume clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/scrm44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.c

## Purpose
Implements common OMAP2/3 SMS/SDRC initialization and SMS context save/restore for SDRAM controller support.

## APIs, Flow, And State
Global state includes `omap2_sdrc_base`, `omap2_sms_base`, static SDRC init parameter pointers for CS0/CS1, and `sms_context.sms_sysconfig`. `omap2_set_globals_sdrc(sdrc, sms)` stores base addresses. `omap2_sdrc_init(sdrc_cs0, sdrc_cs1)` programs SMS and SDRC smart-idle modes, records timing parameter tables, writes SDRC power policy with external clock disable and page policy set, avoids `PWDENA` due to OMAP34xx erratum 1.150, and saves SMS context. `omap2_sms_restore_context()` restores `SMS_SYSCONFIG` after off mode.

## Dependencies And Integration
Depends on `sdrc.h` inline MMIO accessors, common clock setup, and board/platform timing data. Integrates with low-level suspend assembly and SRAM SDRC reprogramming code.

## Risks And Test Signals
SDRAM controller programming is memory-corruption sensitive; comments explicitly avoid a known erratum. Test signals are stable memory under idle/off-mode, SMS context restoration, and boot on platforms with one or two chip selects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.h

## Purpose
Declares OMAP2/3 SDRC/SMS MMIO accessors, SDRC timing data structures, initialization/reprogramming APIs, register offsets, power-control fields, and reference refresh constants.

## APIs, Flow, And State
Outside assembly, the header exports global base pointers, address macros, inline `sdrc_read/write_reg()` and `sms_read/write_reg()`, `omap2_set_globals_sdrc()`, `struct omap_sdrc_params`, `omap2_sdrc_init()`, `omap2_sms_restore_context()`, `struct memory_timings`, and OMAP2xxx SDRC DLL/reprogramming APIs. In assembly, it provides physical address macros. Register offsets cover SDRC sysconfig, chip select config, DLL A/B control/status, power, mode/config/timing/refresh/manual registers for CS0/CS1, and SMS sysconfig. Constants describe DLL lock minimum frequency, fixed-point scaling, stabilization loops, and refresh values.

## Dependencies And Integration
Included by `sdrc.c`, `sdrc2xxx.c`, and OMAP2/3 sleep assembly. It bridges C SDRC initialization with SRAM/assembly suspend code that must access registers while caches/MMU may be constrained.

## Risks And Test Signals
The timing constants are hardware- and board-sensitive, and comments note that optimal refresh values are not universal. Test signals are SDRC DLL lock status, DPLL rate changes, memory stability at low/high frequencies, and off-mode resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc2xxx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc2xxx.c

## Purpose
Implements OMAP2xxx SDRAM timing and DLL handling used during CORE DPLL rate changes.

## APIs, Flow, And State
State includes static `struct memory_timings mem_timings` and `curr_perf_level`. `omap2xxx_sdrc_dll_is_unlocked()` checks the DLLA control unlock bit. `omap2xxx_sdrc_reprogram(level, force)` selects slow or fast DLL control for `CORE_CLK_SRC_DPLL` vs `CORE_CLK_SRC_DPLL_X2`, writes PRCM voltage setup, calls `omap2_sram_reprogram_sdrc()` with interrupts disabled, and updates current performance level. `omap2xxx_sdrc_init_params(force_lock_to_unlock_mode)` detects SDR vs DDR, chooses base chip select, reads current DLL control/status, derives fast and slow DLL values, and calls SRAM initialization to calibrate slow DLL control.

## Dependencies And Integration
Depends on SoC detection, PRM2xxx voltage setup registers, SDRC accessors, clock constants, and SRAM helper routines. Used by the clock framework during OMAP2 CORE DPLL changes.

## Risks And Test Signals
The code disables interrupts and changes memory controller timing from SRAM; mistakes can crash the system immediately. It writes raw PRCM voltage setup addresses with a TODO to abstract through PRM. Test signals are successful CORE DPLL transitions, correct DLL lock/unlock status, and memory stability after frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc2xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep24xx.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep24xx.S

## Purpose
Provides OMAP24xx low-level CPU suspend code that puts SDRC into self-refresh, executes WFI, and restores SDRC/DLL state on wake.

## APIs, Flow, And State
Exports `omap24xx_cpu_suspend` and `omap24xx_cpu_suspend_sz`. Inputs are the pre-sleep DLL control value, `SDRC_DLLA_CTRL`, and `SDRC_POWER` addresses in `r0-r2`. Flow saves registers, issues cache/write barriers, sets SDRC self-refresh-on-idle, waits for interrupt, delays for DPLL/DLL relock, clears self-refresh, touches SDRC memory to restart refresh, rewrites DLLA/DLLB when DDR is used, delays again, and returns.

## Dependencies And Integration
Includes OMAP24xx and SDRC register definitions. This function is copied/called by OMAP2 PM code during deep sleep and relies on SDRC base/timing setup from the SDRC C code.

## Risks And Test Signals
The code depends on fixed delay loops and comments describe early 242x oscillator timing errata. Any wrong register address or DLL value risks memory corruption after wake. Test signals are OMAP24xx deep sleep/resume, DDR vs SDR behavior, and absence of post-resume memory faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep24xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep33xx.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep33xx.S

## Purpose
Implements AM33xx SRAM-resident WFI and deep-sleep resume code, coordinating cache shutdown, EMIF self-refresh/context save, EMIF clock gating, WKUP_M3 signaling, and resume back to `cpu_resume`.

## APIs, Flow, And State
Exports `am33xx_do_wfi`, `am33xx_resume_offset`, `am33xx_resume_from_deep_sleep`, `am33xx_pm_sram`, `am33xx_pm_ro_sram_data`, and `am33xx_do_wfi_sz`. `am33xx_do_wfi` stores WFI flags in SRAM data, optionally flushes/inhibits caches, enters EMIF self-refresh, saves EMIF context, disables EMIF clock, optionally disables MPU clock mode to wake M3, executes barriers and WFI, then handles abort/late interrupt by re-enabling MPU/EMIF, aborting self-refresh, restoring cache enable, and returning `1`. Deep-sleep resume re-enables EMIF, restores EMIF context, exits self-refresh, and branches to physical `cpu_resume` with `r0 = 0`.

## Dependencies And Integration
Depends on `pm33xx` WFI flags, TI EMIF SRAM function table offsets, CM33xx register addresses, and `pm-asm-offsets.h` for SRAM data layout. Integrates with wkup_m3 firmware and EMIF SRAM helper code.

## Risks And Test Signals
Ordering around cache disable, EMIF self-refresh, and clock gating is critical because DDR may be unavailable. Test signals are AM33xx suspend abort handling, successful deep-sleep resume, EMIF context restoration, WKUP_M3 wake events, and no cache/MMU faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep33xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep34xx.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep34xx.S

## Purpose
Provides OMAP34xx/36xx low-level suspend and restore code for retention/off modes, including secure RAM context save, cache handling, SDRC self-refresh/DLL recovery, ROM-code restore entry points, and SDRC errata workarounds.

## APIs, Flow, And State
Exports `enable_omap3630_toggle_l2_on_restore`, `save_secure_ram_context`, `omap34xx_cpu_suspend`, `omap3_do_wfi`, `omap3_do_wfi_sz`, `omap3_restore_es3`, `omap3_restore_3630`, `omap3_restore`, `es3_sdrc_fix`, and `es3_sdrc_fix_sz`. Suspend flow selects SRAM WFI when no context is lost, otherwise flushes caches, disables the C bit, invalidates cache, and enters WFI code. WFI flow sets SDRC self-refresh-on-idle, executes WFI, waits for DPLL3 and SDRC readiness, clears self-refresh, waits/kicks DLL if needed, re-enables cache, and returns for non-off modes. OFF-mode restore is entered by ROM, handles ES3 SDRC erratum i443, OMAP3630 RTA disable, L2 invalidate/secure service calls, scratchpad state, optional L2 aux restore, and branches to `cpu_resume`.

## Dependencies And Integration
Uses OMAP34xx PRM/CM/SDRC/control/SRAM physical addresses, secure monitor calls, scratchpad memory, and generic ARM resume. It is copied partly to internal SRAM by PM setup code.

## Risks And Test Signals
This is highly silicon-revision-specific and runs with MMU/cache constraints. Bad scratchpad, secure monitor, or SDRC sequencing causes resume failure or memory corruption. Test signals are OMAP3430 ES3 off-mode, OMAP3630 L2 restore toggling, secure device suspend, SDRC DLL relock, and resume through `cpu_resume`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep34xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep43xx.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep43xx.S

## Purpose
Implements AM43xx low-level suspend and deep-sleep resume code, extending AM33xx-style EMIF handling with L2X0 cache state, MPU clockdomain sleep, RTC-only power-down support, and EMIF hardware leveling on resume.

## APIs, Flow, And State
Exports `am43xx_do_wfi`, `am43xx_resume_offset`, `am43xx_resume_from_deep_sleep`, `am43xx_emif_sram_table`, `am43xx_pm_sram`, `am43xx_pm_ro_sram_data`, and `am43xx_do_wfi_sz`. Entry flow stores flags, optionally obtains L2 base, flushes/invalidates caches and L2 state into SRAM data, refreshes RTC virtual address translations for RTC-only mode, enters EMIF self-refresh and saves context, disables EMIF, optionally programs RTC PMIC power/wakeup and waits, optionally signals WKUP_M3 by disabling MPU and setting MPU CLKSTCTRL to SW_SLEEP, then WFI. Abort path restores MPU/EMIF/cache and aborts self-refresh. Deep resume sets MPU CLKSTCTRL back to HW_AUTO, powers down EMIF until context restore, re-enables EMIF, restores/exits self-refresh, disables EMIF poweroff, runs hardware leveling, restores/enables L2 via secure monitor calls, and jumps to `cpu_resume`.

## Dependencies And Integration
Depends on AM43xx CM/PRM offsets, `pm33xx` flags, EMIF SRAM helpers, L2X0 registers, OMAP4 secure monitor indices, RTC PMIC registers, and `pm-asm-offsets.h` SRAM layouts.

## Risks And Test Signals
RTC-only mode intentionally powers down via PMIC and waits on RTC seconds, so register accessibility and TLB priming matter. L2 restore depends on secure monitor services. Test signals are AM43xx RTC+DDR and deep-sleep resume, EMIF hardware leveling, L2 cache enable path, WKUP_M3 wake, and abort return path with `r0 = 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep43xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep44xx.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep44xx.S

## Purpose
Implements OMAP44xx SMP/PM low-level suspend finisher, CPU resume entry, and common WFI helper for MPUSS low-power states.

## APIs, Flow, And State
Exports `omap4_finish_suspend`, `omap4_cpu_resume`, and `omap_do_wfi` when SMP/PM conditions apply, with `omap_do_wfi` always present. `omap4_finish_suspend(cpu_state)` handles cache flush/invalidate, secure L1 clean on HS devices, disables data cache, moves CPU out of coherency through SCU power mode or secure monitor, clears SMP bit when allowed, optionally cleans/invalidates L2X0 when the SAR-saved L2 state requires it, then executes WFI. If WFI returns without dormant/off transition, it re-enables cache/coherency and normal SCU state. `omap4_cpu_resume` is ROM-entered from dormant/off, enables NS SMP access on HS CPU1 when needed, restores/enables L2X0 from SAR RAM through secure monitor calls, then branches to `cpu_resume`. `omap_do_wfi` drains interconnect when configured, executes barriers, WFI, and post-WFI NOPs.

## Dependencies And Integration
Depends on OMAP secure monitor APIs, SAR RAM layout, SCU, PL310/L2X0 registers, generic ARM `cpu_resume`, and optional interconnect barrier support. Integrated with OMAP4 CPU idle/suspend and ROM wakeup programming.

## Risks And Test Signals
The code runs with caches/coherency disabled and cannot use ordinary locking. GP vs HS device paths differ, and secure monitor API availability is required for HS/L2 paths. Test signals are OMAP4 MPUSS CSWR/OSWR/OFF transitions, CPU1 resume, L2 cache restoration, no deadlocks in non-coherent mode, and correct fallback when WFI returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep44xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/smartreflex-class3.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/smartreflex-class3.c

## Purpose
Registers SmartReflex Class 3 behavior for OMAP voltage adaptation using error generation and the voltage processor.

## APIs, Flow, And State
Static callbacks implement `enable`, `disable`, and `configure` for `struct omap_sr_class_data`. Enable reads the current voltage from the voltage domain, refuses with `-ENODATA` if unknown, enables the voltage processor, then calls `sr_enable(sr, volt)`. Disable turns off SR error generation, disables the VP, disables SR, and optionally resets the voltage domain. Configure delegates to `sr_configure_errgen()`. `sr_class3_init()` registers the class at OMAP late init.

## Dependencies And Integration
Depends on Linux SmartReflex APIs, OMAP SoC initcall gating, and OMAP voltage-domain/VP helpers. It integrates with SmartReflex core registration through `sr_register_class()`.

## Risks And Test Signals
Enabling without a known voltage is blocked, but VP/SR sequencing still affects live voltage control. Test signals are late init registration, SmartReflex enable/disable cycles, voltage reset behavior, and no warnings about unknown current voltage during normal operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/smartreflex-class3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/soc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/soc.h

## Purpose
Defines OMAP2+ SoC identity, revision, class/subclass/package detection macros, feature flags, revision constants, and OMAP-scoped initcall wrappers.

## APIs, Flow, And State
Declares `omap_type()` and `omap_rev()`, then derives class, AM/TI/DRA class, subclass, package, and specific type predicates through macro-generated inline functions. Kconfig-controlled `soc_is_*()` macros default to `0` and are selectively redefined when a SoC family is enabled. Revision constants encode OMAP242x/243x/343x/363x, TI81xx, AM35xx/33xx/43xx, OMAP443x/446x/447x/54xx, and DRA7xx variants. Feature state is global `omap_features`, with helpers such as `omap3_has_io_wakeup()`, `omap3_has_sdrc()`, and `omap4_has_perf_silicon()`. `omap_*_initcall()` wrappers skip init functions when a multiplatform kernel is booted on a non-OMAP SoC. Legacy `cpu_is_*()` macros alias modern `soc_is_*()`.

## Dependencies And Integration
Includes per-family ID headers, Linux bitops, and OF support. Used throughout PRM/CM/PM/SDRC code to select SoC-specific register layouts and errata paths.

## Risks And Test Signals
The macro layering is compile-time and runtime dependent; wrong `omap_rev()` encoding or Kconfig guard can disable valid SoC paths or enable invalid ones. Test signals are revision detection during boot, correct SoC-specific PRM init data selection, feature-dependent IO wake/SDRC behavior, and initcalls not running on non-OMAP multiplatform boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/soc.h -->
