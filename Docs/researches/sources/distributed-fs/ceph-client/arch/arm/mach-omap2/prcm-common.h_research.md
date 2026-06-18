# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm-common.h

## Purpose
Defines PRCM module offsets, shared PRM/CM bit masks, common timeout helpers, PRCM interrupt metadata, and PRCM init-data structures used across OMAP2/3/4-era ARM SoCs. It is the shared vocabulary that lets SoC-specific PRM, CM, wakeup, and device-tree init code refer to hardware registers consistently.

## APIs, Flow, And State
The file is mostly declarative macros for module offsets and bitfields: OCP/MPU/CORE/GFX/WKUP/PLL plus OMAP24xx, OMAP3430, TI81xx, enable/status/wakeup bits, IO-chain masks, and dependency bits. Runtime-facing APIs include `omap_test_timeout(cond, timeout, index)`, `struct omap_prcm_irq`, `struct omap_prcm_irq_setup`, `OMAP_PRCM_IRQ`, `struct omap_domain_base`, and `struct omap_prcm_init_data`. The PRCM IRQ setup structure carries hardware register offsets, callback hooks, saved IRQ masks, priority masks, base IRQ allocation, and suspend flags that are populated by `prm_common.c`.

## Dependencies And Integration
Included by almost every file in this set. Depends on Linux delay APIs outside assembly and on `bool`, `u*`, `s*`, `__iomem`, and device-tree types via the including context. Its data structures connect SoC PRM implementations to the common chained IRQ code and to `omap2_prm_base_init()` discovery.

## Risks And Test Signals
Incorrect bit masks or offsets can break low-level clock, reset, wakeup, or power-domain transitions across many SoCs. The duplicated `OMAP3430_EN_GPT12` define and comments about possible TI documentation bugs are maintenance hazards. Test signals are boot on affected SoCs, PRCM IRQ delivery, suspend/resume with IO wakeups, reset-source reporting, and successful powerdomain transitions without timeout warnings.
