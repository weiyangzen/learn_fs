# sources/distributed-fs/ceph-client/include/linux/mmc/pm.h

## Purpose
`mmc/pm.h` provides shared power-management flag definitions for MMC hosts, core code, SDIO core, and SDIO function drivers. It exists so all layers use the same suspend capability/request bits.

## Important APIs, Types, And Functions
The file defines `mmc_pm_flag_t` and two flags: `MMC_PM_KEEP_POWER`, requesting card power preservation across suspend, and `MMC_PM_WAKE_SDIO_IRQ`, requesting SDIO IRQ wake capability during suspend.

## Control Flow And State
There is no direct control flow. The flags become persistent host and function state through `mmc_host::pm_caps`, `mmc_host::pm_flags`, and SDIO PM helper calls. Suspend/resume paths test these bits to decide whether to power-cycle cards and whether SDIO IRQs may wake the system.

## Dependencies And Integration Points
This header is intentionally standalone and is included by MMC host and SDIO function headers. Integration points include host PM capability declaration, SDIO function driver PM requests, system suspend, runtime PM, wakeup-source handling, and card power sequencing.

## Risks And Test Signals
Risks include hosts advertising unsupported wake/power retention, SDIO drivers requesting flags outside host capabilities, and suspend paths dropping card state despite `KEEP_POWER`. Test signals include suspend/resume with SDIO wake, power-retention tests on removable and nonremovable cards, host capability masking tests, and SDIO driver PM negotiation tests.
