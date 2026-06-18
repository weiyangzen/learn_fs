<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-pm.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-pm.c

## Purpose
Implements XO-1 suspend-to-RAM wake mask programming and CS5536-based poweroff.

## Important APIs, Types, And Functions
Exports `olpc_xo1_pm_wakeup_set()` and `olpc_xo1_pm_wakeup_clear()` to let RTC/SCI code alter `wakeup_mask`. `xo1_power_state_enter()` invokes `do_olpc_suspend_lowlevel()`. `xo1_do_sleep()` programs wake enables and calls the OpenFirmware BIOS entry. `xo1_power_off()` writes CS5536 PM registers.

## Control Flow
Two platform drivers collect PMS and ACPI base I/O resources. Once both bases are known on an OLPC machine, the driver installs suspend ops and `pm_power_off`. Suspend saves SCI mask, enters low-level assembly, resumes, and restores the mask.

## State And Persistence
Stores `acpi_base`, `pms_base`, and `wakeup_mask`. Hardware PM registers hold wake configuration across sleep entry.

## Dependencies And Integration Points
Depends on CS5536 register definitions, OLPC machine detection, OLPC OpenFirmware entry, generic suspend ops, and sibling XO-1 SCI/RTC wake-mask users.

## Risks And Edge Cases
Only `PM_SUSPEND_MEM` is valid. Calling firmware with inline assembly is fragile and 32-bit-specific. Remove sets `pm_power_off = NULL` rather than restoring a prior handler.

## Test Signals
XO-1 suspend/resume, wake by power button/RTC/lid as configured, and poweroff register sequencing are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-pm.c -->
