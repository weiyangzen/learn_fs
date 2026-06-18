# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.c

## Purpose
Implements AM33xx PRM operations for register access, hardreset control, powerdomain callbacks, reboot, and powerdomain context save/restore.

## APIs, Flow, And State
Static accessors read/write/RMW `prm_base.va + inst + idx`. Hardreset functions mirror OMAP4-style sequencing: test reset bit, clear status, deassert control, then poll status with `MAX_MODULE_HARDRESET_WAIT`. Powerdomain operations set/read next/current power state, request low-power state changes, clear previous state, set/read logic retention and memory bank states using per-domain masks, and poll `OMAP_INTRANSITION_MASK`. `am33xx_prm_global_sw_reset()` selects warm reset by default and cold reset when `prm_reboot_mode == REBOOT_COLD`. Context persistence is stored in `pwrdm->context`, with `LOWPOWERSTATECHANGE` masked out before restore.

## Dependencies And Integration
Depends on `powerdomain`, `prm33xx.h`, and AM33xx bit definitions. Registers `am33xx_prm_ll_data` with common PRM code and exposes `am33xx_pwrdm_operations` to the powerdomain layer. Integrates with Linux reboot modes.

## Risks And Test Signals
Array-indexed powerdomain masks must be valid for the requested memory bank. Context restore compares current state and saved control state before waiting, so incorrect offsets can cause missed waits or hangs. Test signals are AM33xx suspend/resume, RTC/DDR modes, hardreset users, and cold-vs-warm reboot behavior.
