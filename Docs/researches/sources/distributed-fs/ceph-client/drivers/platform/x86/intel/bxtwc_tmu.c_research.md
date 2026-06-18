<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bxtwc_tmu.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bxtwc_tmu.c

## Purpose
Adds Broxton Whiskey Cove PMIC Time Management Unit alarm interrupt support, primarily enabling alarm wakeup behavior.

## Important APIs, Types, And Functions
`struct wcove_tmu` stores IRQ and PMIC regmap. `bxt_wcove_tmu_irq_handler()` reads `BXTWC_TMUIRQ`, acknowledges wake/system alarm bits, and returns whether it handled the IRQ. Probe requests a threaded IRQ and unmasks second-level TMU alarm bits. Remove masks TMU interrupts at level 1 and second level.

## Control Flow
The platform driver gets the parent `intel_soc_pmic` regmap, requests IRQ 0, unmasks `BXTWC_TMU_WK_ALRM` and `BXTWC_TMU_SYS_ALRM`, and stores driver data. Suspend enables IRQ wake; resume disables it.

## State And Persistence
State is the PMIC interrupt mask and pending-status registers plus the IRQ wake setting. Device memory is devm-managed.

## Dependencies And Integration Points
Depends on `INTEL_SOC_PMIC_BXTWC`, `MFD_INTEL_PMC_BXT`, regmap, platform IRQs, and PM sleep.

## Risks And Test Signals
Risks are missed alarm acknowledgements, incorrect mask restoration on remove, and unchecked regmap failures. Test by programming PMIC alarms, verifying wake from suspend, checking no IRQ storm, and confirming masks are restored after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bxtwc_tmu.c -->
